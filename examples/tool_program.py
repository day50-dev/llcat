#!/usr/bin/env python3
import json, sys, os, subprocess
from pathlib import Path

def rpc(data):
    print(json.dumps({"jsonrpc": "2.0", "result": data}), flush=True)
    sys.exit(0)

tool_name = None
while res := sys.stdin.readline():
    input_data = json.loads(res)
    if input_data['method'] == 'initialize':
        print('{"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":true},"resources":{"listChanged":true},"completions":{}},"serverInfo":{"name":"tool demo","version":"1.0.0"}},"jsonrpc":"2.0","id":1}', flush=True)
        continue

    if input_data['method'] != 'tools/call':
        continue

    params = input_data.get('params')
    tool_name = params['name']
    args = params.get('arguments', {})
    break

if tool_name == "list_mp3s":
    MP3_DIR = Path(args.get('path') or '.').expanduser()
    mp3s = [f.name for f in MP3_DIR.rglob("*.mp3")]
    rpc(mp3s)

elif tool_name == "play_mp3":
    filename = args['filename']
    subprocess.Popen(['mpv', '--quiet', Path(args.get('path') or '.').expanduser() / filename])
    rpc({"status": "playing", "file": filename})

sys.exit(1)
