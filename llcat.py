#!/usr/bin/env python3
import sys, requests, json, argparse, subprocess, select, importlib.metadata, traceback, os
import logging

logging.basicConfig(level=(os.environ.get('LOGLEVEL') or 'warning').upper())

VERSION = None
SHUTUP = []

def create_content_with_attachments(text_prompt, attachment_list):
    import base64, re
    content = []
    
    for file_path in attachment_list:
        file_data = safeopen(file_path, what='attachment', fmt='bin')
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        prefix = "image" if re.match(r'((we|)bm?p|j?p[en]?g)', ext) else "application"
        
        content.append({
            'type': 'document' if prefix == "application" else "image",
            'source': {
                'type': 'base64',
                'media_type': f"{prefix}/{ext}",
                'data': base64.b64encode(file_data).decode('utf-8')
            }
        })
    
    if text_prompt:
        content.append({
            'type': 'text',
            'text': text_prompt
        })
    
    return content if len(content) > 1 else text_prompt

def maybejson(txt):
    try:
        return json.loads(txt)
    except:
        return txt

def safeopen(path, what='cli', fmt='json', can_create=False):
    try:
        flags = 'rb' if fmt == 'bin' else 'r'

        if(os.path.exists(path)) or can_create:
            if can_create:
                fd = os.open(path, os.O_RDONLY | os.O_CREAT, mode=0o644)
            else:
                fd = os.open(path, os.O_RDONLY)

            with os.fdopen(fd, flags) as f:
                if fmt == 'json':
                    try:
                        return json.load(f)
                    except Exception as ex:
                        if can_create and os.path.getsize(path) == 0:
                            return [] 
                        err_out(what=what, message=f"{path} is unparsable: {ex}", code=2)

                return f.read()

        err_out(what=what, message=f"{path} is an invalid or inaccessible path", code=2)

    except Exception as ex:
        err_out(what=what, message=f"{path} cannot be loaded", obj=traceback.format_exc(), code=126)

def safecall(base_url, req = None, headers = {}, what = "post", transport="openai"):
    headers['User-Agent'] = headers['X-Title'] = 'llcat'
    headers['HTTP-Referer'] = 'https://github.com/day50-dev/llcat'

    try:
        logging.debug(f"request {req}")
        if what == 'post':
            if transport == 'ollama':
                if req and 'messages' in req:
                    req = req.copy()
                    new_msgs = []
                    for m in req['messages']:
                        nm = {'role': m['role']}
                        if isinstance(m.get('content'), list):
                            txt = []
                            imgs = []
                            for c in m['content']:
                                if c.get('type') == 'text':
                                    txt.append(c.get('text', ''))
                                elif c.get('type') == 'image' and 'source' in c:
                                    imgs.append(c['source']['data'])
                            nm['content'] = '\n'.join(txt)
                            if imgs:
                                nm['images'] = imgs
                        else:
                            nm['content'] = m.get('content')
                        new_msgs.append(nm)
                    req['messages'] = new_msgs

                r = requests.post(f'{base_url}/api/chat', json=req, headers=headers, stream=True)
            else:
                r = requests.post(f'{base_url}/chat/completions', json=req, headers=headers, stream=True)
        else:
            r = requests.get(base_url, headers=headers, stream=True)

        r.raise_for_status()  

    except Exception as e:
        obj = {'request': req, 'response': {}}

        if hasattr(e, 'response') and e.response is not None:
            obj['response']['status_code'] = e.response.status_code
            try:
                error_data = e.response.json()
                obj['response']['payload'] = error_data
            except:
                obj['response']['payload'] = e.response.text

        err_out(what='response', message=str(e), obj=obj)
    return r

def mcp_start(server_config):
    """Start MCP server and return (proc, rpc)"""
    sub_env = os.environ.copy()
    sub_env.update(server_config.get('env') or {})

    cmd = [server_config['command']] + server_config['args']
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=sub_env
    )

    id = 0
    def rpc(method, params=None):
        nonlocal id
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            id += 1
            msg["params"] = params
            msg["id"] = id

        proc.stdin.write(json.dumps(msg) + '\n')

    rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "llcat", "version": "1.0"}})
    rpc("notifications/initialized")

    proc.stdin.flush()  

    rlist, _, _ = select.select([proc.stderr, proc.stdout], [], [], 10.0)
    if proc.stderr in rlist:
        err_out(what="toolcall", message=proc.stderr.readline(), obj=cmd)
    if proc.stdout in rlist:
        proc.stdout.readline()

    return proc, rpc

def mcp_finish(proc):
    """Flush, read response, terminate, return parsed JSON"""
    try:
        proc.stdin.flush()
    except:
        pass

    res_json = None
    response = None
    rlist, _, _ = select.select([proc.stdout], [], [], 10.0)

    if rlist:
        response = proc.stdout.readline()
        try:
            res_json = json.loads(response)
        except:
            pass
    else:
        rlist, _, _ = select.select([proc.stderr], [], [], 0.0)
        if proc.stderr in rlist:
            response = proc.stderr.readline()
            proc.terminate()
            err_out(what="toolcall", message=response)

    proc.terminate()
    if res_json:
        return res_json.get('result', {})
    return response

def discover_tools(server_config):
    proc, rpc = mcp_start(server_config)
    rpc("tools/list", {})
    res = mcp_finish(proc)
    if type(res) is str: 
        return res
    return res.get('tools')

def call_tool(server_config, tool_name, arguments):
    if type(arguments) is str:
        arguments = json.loads(arguments)

    proc, rpc = mcp_start(server_config)
    rpc("tools/call", {"name": tool_name, "arguments": arguments})
    return mcp_finish(proc)

mcp_dict_ref = {}
def mcp_get_def(path):
    import re
    config = safeopen(path)

    global mcp_dict_ref
    tool_return = []
    for server_name, server_config in config.get('mcpServers').items():
        safe_name = re.sub(r'[^a-z0-9_]', '_', server_name.lower())
        counter = 0
        
        tool_dict = discover_tools(server_config)
        for tool in tool_dict:
            base_name = f"{safe_name}_{tool['name']}"
            llm_tool_name = base_name
            
            while llm_tool_name in mcp_dict_ref:
                llm_tool_name = f"{base_name}{counter}"
                counter += 1
            
            mcp_dict_ref[llm_tool_name] = (server_config, tool['name'])
            tool['name'] = llm_tool_name
            tool['parameters'] = tool['inputSchema']
            del tool['inputSchema']

            tool_return.append({'type': 'function', 'function': tool})

    return tool_return
        
def err_out(what="general", message="", obj=None, code=1):
    if not set(['error',what]).intersection(SHUTUP):
        fulldump={'data': obj, 'level': 'error', 'class': what, 'message': message}
        print(json.dumps(fulldump), file=sys.stderr)
    sys.exit(code)

def tool_gen(res, transport="openai"):
    for line in res.iter_lines():
        if line:
            line = line.decode('utf-8')
            logging.debug(f"response: {line}")
            if transport == 'ollama':
                try:
                    obj = json.loads(line)
                    delta = {}
                    if 'message' in obj:
                        msg = obj['message']
                        if 'content' in msg:
                            delta['content'] = msg['content']
                        if 'tool_calls' in msg:
                             tc_list = []
                             for i, tc in enumerate(msg['tool_calls']):
                                 tc_list.append({
                                     'index': i,
                                     'id': 'call_'+str(i), 
                                     'function': {
                                         'name': tc['function']['name'],
                                         'arguments': json.dumps(tc['function']['arguments'])
                                     }
                                 })
                             delta['tool_calls'] = tc_list
                    
                    if delta:
                        yield json.dumps({'choices': [{'delta': delta}]})
                    
                    if obj.get('done'):
                        break
                except:
                    pass
            elif line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    break
                yield data

def main():
    global VERSION, mcp_dict_ref 
    VERSION = importlib.metadata.version('llcat')
    parser = argparse.ArgumentParser()

    # We want to show things in the order of importance
    parser.add_argument('-su', '-u', '--server_url', help='Server URL (e.g., http://::1:8080)')
    parser.add_argument('-t', '--transport', default='openai', choices=['openai', 'ollama'], help='Transport to use (openai or ollama)')
    parser.add_argument('-sk', '-k', '--server_key', help='Server API key for authorization')

    parser.add_argument('-m',  '--model', nargs='?', const='', help='Model to use (or list models if no value)')
    parser.add_argument('-s',  '--system', help='System prompt')

    parser.add_argument('-c',  '--conversation', help='Conversation history file')
    parser.add_argument('-cr', action='store_true', help="Do not write anything back to the conversation file")
    parser.add_argument('-mf', '--mcp_file', help='MCP file to use')
    parser.add_argument('-tf', '--tool_file', help='JSON file with tool definitions')
    parser.add_argument('-tp', '--tool_program', help='Program to execute tool calls')
    parser.add_argument('-a',  '--attach', action='append', help='Attach file(s)')
    parser.add_argument('-bq', '--be_quiet', action='append', help='Make it shutup about things')
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    parser.add_argument('user_prompt', nargs='*', help='Your prompt')
    args = parser.parse_args()

    if args.be_quiet:
        global SHUTUP
        SHUTUP = set((','.join(args.be_quiet)).split(','))

    # Server and headers
    if args.server_url:
        if args.transport == 'ollama':
             base_url = args.server_url.rstrip('/')
        else:
             base_url = args.server_url.rstrip('/').rstrip('/v1') + '/v1'
    elif args.transport == 'ollama':
        base_url = 'http://localhost:11434'
    else:
        parser.print_help()
        err_out(what="cli", message="No server URL specified", code=2)

    headers = {'Content-Type': 'application/json'}
    if args.server_key:
        headers['Authorization'] = f'Bearer {args.server_key}'

    # Prompt 
    cli_prompt = ' '.join(args.user_prompt) if args.user_prompt else ''
    stdin_prompt = sys.stdin.read() if select.select([sys.stdin], [], [], 0.0)[0] else ''

    if len(stdin_prompt) and len(cli_prompt):
        prompt = f"<ask>{cli_prompt}</ask><content>{stdin_prompt}</content>"
    else:
        prompt = cli_prompt + stdin_prompt

    # Model
    if not args.model or (len(prompt) == 0 and not args.conversation):
        if args.transport == 'ollama':
             r = safecall(base_url=f'{base_url}/api/tags', headers=headers, what='get', transport=args.transport)
        else:
             r = safecall(base_url=f'{base_url}/models', headers=headers, what='get', transport=args.transport)

        try:
            resp = r.json()
            models = []
            if 'data' in resp:
                models = resp['data']
            elif 'models' in resp:
                for m in resp['models']:
                    models.append({'id': m['name']})
            
            for model in models:
                if args.model == '':
                    print(model['id'])
                elif args.model in [model['id'], '*']:
                    print(json.dumps(model))
            sys.exit(0)
        except Exception as ex:
            err_out(what="parsing", message=f"{base_url}/models is unparsable json: {ex}", obj=r.text, code=126)

    # Conversation
    messages = safeopen(args.conversation, can_create=True) if args.conversation else []

    # Tools
    tools = safeopen(args.tool_file) if args.tool_file else None
    
    if tools:
        for tool in tools:
            mcp_dict_ref[tool['function']['name']] = ({'command':'python','args':[args.tool_program]}, tool['function']['name'])

    if args.mcp_file:
        tools = tools or []
        tools += mcp_get_def(args.mcp_file)

    # Attachment
    message_content = create_content_with_attachments(prompt, args.attach) if args.attach else prompt

    # System Prompt
    if args.system:
        if len(messages) > 0: 
            if messages[0].get('role') != 'system':
                messages.insert(0, {})
            messages[0] = {'role': 'system', 'content': args.system}
        else:
            messages.append({'role': 'system', 'content': args.system})

    messages.append({'role': 'user', 'content': message_content})

    # Request construction
    req = {'messages': messages, 'stream': True}
    if args.model:
        req['model'] = args.model
    if tools:
        req['tools'] = tools

    # The actual call
    r = safecall(base_url,req,headers, transport=args.transport)

    assistant_response = ''
    tool_call_list = []
    current_tool_call = None

    # tool_call is two calls
    for data in tool_gen(r, transport=args.transport):
        try:
            chunk = json.loads(data)
            delta = chunk['choices'][0]['delta']
            content = delta.get('content', '')
            if content:
                print(content, end='', flush=True)
                assistant_response += content
            
            if 'tool_calls' in delta:
                for tc in delta['tool_calls']:
                    idx = tc.get('index', 0)
                    if idx >= len(tool_call_list):
                        tool_call_list.append({'id': '', 'type': 'function', 'function': {'name': '', 'arguments': ''}})
                        current_tool_call = tool_call_list[idx]
                    
                    if 'id' in tc:
                        tool_call_list[idx]['id'] = tc['id']
                    if 'function' in tc:
                        for key in ['name','arguments']:
                            if key in tc['function']:
                                tool_call_list[idx]['function'][key] += tc['function'][key]

        except Exception as ex:
            err_out(what="toolcall", message=traceback.format_exc(), obj=data)

    if tool_call_list or args.tool_program:
        for tool_call in tool_call_list:
            fname = tool_call['function']['name']
            
            if not set(['toolcall','debug','request']).intersection(SHUTUP):
                print(json.dumps({'level':'debug', 'class': 'toolcall', 'message': 'request', 'obj': tool_call}), file=sys.stderr)
            
            if args.tool_program and '/' not in args.tool_program:
                args.tool_program = './' + args.tool_program

            config, name = mcp_dict_ref[fname]
            result = json.dumps( call_tool(config, name, tool_call['function']['arguments']))

            if not set(['toolcall','debug','result']).intersection(SHUTUP):
                print(json.dumps({'level':'debug', 'class': 'toolcall', 'message': 'result', 'obj': maybejson(result)}), file=sys.stderr)
            
            messages.extend([{
                'role': 'assistant',
                'content': assistant_response if assistant_response else None,
                'tool_calls': tool_call_list
            }, {
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': result
            }])
        
        req = {'messages': messages, 'stream': True}
        if args.model:
            req['model'] = args.model
        if tools:
            req['tools'] = tools
        
        r = safecall(base_url,req,headers, transport=args.transport)

        assistant_response = ''
        for data in tool_gen(r, transport=args.transport):
            try:
                chunk = json.loads(data)
                content = chunk['choices'][0]['delta'].get('content', '')
                if content:
                    print(content, end='', flush=True)
                    assistant_response += content
            except Exception as ex:
                err_out(what="toolcall", message=traceback.format_exc(), obj=data)
        print()

    if args.conversation and not args.cr:
        if len(assistant_response):
            messages.append({'role': 'assistant', 'content': assistant_response})
            try:
                with open(args.conversation, 'w') as f:
                    json.dump(messages, f, indent=2)
            except Exception as ex:
                err_out(what="conversation", message=f"{args.conversation} is unwritable", obj=traceback.format_exc(), code=126)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ex:
        err_out(message=f"Keyboard interrupt")
    #except Exception as ex:
    #    err_out(message=traceback.format_exc()
