#!/usr/bin/env python3
import sys, requests, json, argparse, subprocess, select

def create_content_with_attachments(text_prompt, attachments):
    import base64, re
    content = []
    
    for file_path in attachments:
        try:
            with open(file_path, 'rb') as f:
                ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                prefix = "image" if re.match(r'((we|)bm?p|j?p[en]?g)', ext) else "application"
                
                content.append({
                    'type': 'document' if prefix == "application" else "image",
                    'source': {
                        'type': 'base64',
                        'media_type': f"{prefix}/{ext}",
                        'data': base64.b64encode(f.read()).decode('utf-8')
                    }
                })
        except Exception as ex:
            err_out(what="attachment", message=file_path, obj=str(ex), code=126)
    
    if text_prompt:
        content.append({
            'type': 'text',
            'text': text_prompt
        })
    
    return content if len(content) > 1 else text_prompt

def safecall(base_url, req, headers):
    try:
        r = requests.post(f'{base_url}/chat/completions', json=req, headers=headers, stream=True)
        r.raise_for_status()  
    except requests.exceptions.RequestException as e:
        obj = {'request': req, 'response': {}}
        if hasattr(e, 'response') and e.response is not None:
            obj['response']['status_code'] = e.response.status_code
            try:
                error_data = e.response.json()
                obj['response']['payload'] = error_data
            except:
                obj['response']['payload'] = e.response.text

        err_out(what='response', message=e, obj=obj)
    return r

def err_out(what="general", message="", obj={}, code=1):
    fulldump={'data': obj, 'level': 'error', 'class': what, 'message': message}
    print(json.dumps(fulldump), file=sys.stderr)
    sys.exit(code)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conversation', help='Conversation history file')
    parser.add_argument('-m', '--model', nargs='?', const='', help='Model to use (or list models if no value)')
    parser.add_argument('-k', '--key', help='API key for authorization')
    parser.add_argument('-s', '--server', help='Server URL (e.g., http://::1:8080)')
    parser.add_argument('-p', '--prompt', help='System prompt')
    parser.add_argument('-tf', '--tool_file', help='JSON file with tool definitions')
    parser.add_argument('-tp', '--tool_program', help='Program to execute tool calls')
    parser.add_argument('-a', '--attach', action='append', help='Attach file(s)')
    parser.add_argument('user_prompt', nargs='*', help='Your prompt')
    args = parser.parse_args()

    if args.server:
        base_url = args.server.rstrip('/').rstrip('/v1') + '/v1'
    else:
        parser.print_help()
        err_out(what="cli", message="No server specified", code=2)

    headers = {'Content-Type': 'application/json'}
    if args.key:
        headers['Authorization'] = f'Bearer {args.key}'

    cli_prompt = ' '.join(args.user_prompt) if args.user_prompt else ''
    stdin_prompt = sys.stdin.read() if select.select([sys.stdin], [], [], 0.0)[0] else ''

    if len(stdin_prompt) and len(cli_prompt):
        prompt = f"<ask>{cli_prompt}</ask><content>{stdin_prompt}"
    else:
        prompt = cli_prompt + stdin_prompt

    if args.model == '' and len(prompt) == 0:
        r = requests.get(f'{base_url}/models', headers=headers)
        try:
            models = r.json()
            for model in models.get('data', []):
                print(model['id'])
            sys.exit(0)
        except:
            err_out(what="parsing", message=f"{base_url}/models is unparsable json", obj=r.text, code=126)

    import os
    messages = []
    if args.conversation and os.path.exists(args.conversation):
        with open(args.conversation, 'r') as f:
            try:
                messages = json.load(f)
            except Exception as ex:
                # If it's an empty file, proceed
                if os.path.getsize(args.conversation) == 0:
                    messages = []
                else:
                    err_out(what="parsing", message=f"{args.conversation} is unparsable json", obj=str(ex), code=126)

    # Create message content with attachments if provided
    if args.attach:
        message_content = create_content_with_attachments(prompt, args.attach)
    else:
        message_content = prompt

    messages.append({'role': 'user', 'content': message_content})

    tools = None
    if args.tool_file:
        with open(args.tool_file, 'r') as f:
            tools = json.load(f)

    if args.prompt:
        if messages[0].get('role') != 'system':
            messages.insert(0, {})
        messages[0] = {'role': 'system', 'content': args.prompt}

    req = {'messages': messages, 'stream': True}
    if args.model:
        req['model'] = args.model
    if tools:
        req['tools'] = tools

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
            
            print(json.dumps({'level':'debug', 'class': 'toolcall', 'message': 'request', 'obj': tool_call}), file=sys.stderr)
            
            result = subprocess.run(
                args.tool_program,
                input=tool_input,
                capture_output=True,
                text=True,
                shell=True
            )
            print(json.dumps({'level':'debug', 'class': 'toolcall', 'message': 'result', 'obj': result}), file=sys.stderr)
            
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
                        print(ex)
                        pass
        print()

    if args.conversation:
        if len(assistant_response):
            messages.append({'role': 'assistant', 'content': assistant_response})
            with open(args.conversation, 'w') as f:
                json.dump(messages, f, indent=2)

if __name__ == "__main__":
    main()
