#!/usr/bin/env python3
import sys, requests, json, argparse, subprocess, select, importlib.metadata

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
    import os

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
        err_out(what=what, message=f"{path} cannot be loaded", obj=str(ex), code=126)

def safecall(base_url, req = None, headers = None, what = "post"):
    try:
        if what == 'post':
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

def err_out(what="general", message="", obj=None, code=1):
    fulldump={'data': obj, 'level': 'error', 'class': what, 'message': message}
    print(json.dumps(fulldump), file=sys.stderr)
    sys.exit(code)

def main():
    version = importlib.metadata.version('llcat')
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',  '--conversation', help='Conversation history file')
    parser.add_argument('-m',  '--model', nargs='?', const='', help='Model to use (or list models if no value)')
    parser.add_argument('-sk', '--key', help='Server API key for authorization')
    parser.add_argument('-su', '-u', '--server', help='Server URL (e.g., http://::1:8080)')
    parser.add_argument('-s',  '--system', help='System prompt')
    parser.add_argument('-tf', '--tool_file', help='JSON file with tool definitions')
    parser.add_argument('-tp', '--tool_program', help='Program to execute tool calls')
    parser.add_argument('-a',  '--attach', action='append', help='Attach file(s)')
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    parser.add_argument('user_prompt', nargs='*', help='Your prompt')
    args = parser.parse_args()

    # Server and headers
    if args.server:
        base_url = args.server.rstrip('/').rstrip('/v1') + '/v1'
    else:
        parser.print_help()
        err_out(what="cli", message="No server URL specified", code=2)

    headers = {'Content-Type': 'application/json'}
    if args.key:
        headers['Authorization'] = f'Bearer {args.key}'

    # Prompt 
    cli_prompt = ' '.join(args.user_prompt) if args.user_prompt else ''
    stdin_prompt = sys.stdin.read() if select.select([sys.stdin], [], [], 0.0)[0] else ''

    if len(stdin_prompt) and len(cli_prompt):
        prompt = f"<ask>{cli_prompt}</ask><content>{stdin_prompt}</content>"
    else:
        prompt = cli_prompt + stdin_prompt

    # Model
    if args.model == '' and len(prompt) == 0:
        r = safecall(base_url=f'{base_url}/models', headers=headers, what='get')

        try:
            models = r.json()
            for model in models.get('data', []):
                print(model['id'])
            sys.exit(0)
        except Exception as ex:
            err_out(what="parsing", message=f"{base_url}/models is unparsable json: {ex}", obj=r.text, code=126)

    # Conversation
    messages = safeopen(args.conversation, can_create=True) if args.conversation else []

    # Tools
    tools = safeopen(args.tool_file) if args.tool_file else None

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
    r = safecall(base_url,req,headers)

    assistant_response = ''
    tool_calls = []
    current_tool_call = None

    for line in r.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    break
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
                            if idx >= len(tool_calls):
                                tool_calls.append({'id': '', 'type': 'function', 'function': {'name': '', 'arguments': ''}})
                                current_tool_call = tool_calls[idx]
                            
                            if 'id' in tc:
                                tool_calls[idx]['id'] = tc['id']
                            if 'function' in tc:
                                if 'name' in tc['function']:
                                    tool_calls[idx]['function']['name'] += tc['function']['name']
                                if 'arguments' in tc['function']:
                                    tool_calls[idx]['function']['arguments'] += tc['function']['arguments']
                except:
                    pass

    if args.tool_program and tool_calls:
        for tool_call in tool_calls:
            tool_input = json.dumps({
                'id': tool_call['id'],
                'name': tool_call['function']['name'],
                'arguments': json.loads(tool_call['function']['arguments'])
            })
            
            print(json.dumps({'level':'debug', 'class': 'toolcall', 'message': 'request', 'obj': json.loads(tool_input)}), file=sys.stderr)
            
            if '/' not in args.tool_program:
                args.tool_program = './' + args.tool_program

            result = subprocess.run(
                args.tool_program,
                input=tool_input,
                capture_output=True,
                text=True,
                shell=True
            )
            print(json.dumps({'level':'debug', 'class': 'toolcall', 'message': 'result', 'obj': maybejson(result.stdout)}), file=sys.stderr)
            
            messages.append({
                'role': 'assistant',
                'content': assistant_response if assistant_response else None,
                'tool_calls': tool_calls
            })
            messages.append({
                'role': 'tool',
                'tool_call_id': tool_call['id'],
                'content': result.stdout
            })
        
        req = {'messages': messages, 'stream': True}
        if args.model:
            req['model'] = args.model
        if tools:
            req['tools'] = tools
        
        r = safecall(base_url,req,headers)

        assistant_response = ''
        for line in r.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            print(content, end='', flush=True)
                            assistant_response += content
                    except Exception as ex:
                        err_out(what="toolcall", message=str(ex), obj=data)
        print()

    if args.conversation:
        if len(assistant_response):
            messages.append({'role': 'assistant', 'content': assistant_response})
            try:
                with open(args.conversation, 'w') as f:
                    json.dump(messages, f, indent=2)
            except Exception as ex:
                err_out(what="conversation", message=f"{args.conversation} is unwritable", obj=str(ex), code=126)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ex:
        err_out(message=f"Keyboard interrupt")
    except Exception as ex:
        err_out(message=str(ex))
