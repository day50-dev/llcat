#!/usr/bin/env python3
import json, sys, os, subprocess
from pathlib import Path

while res := sys.stdin.readline():
    try:
        input_data = json.loads(res)
        params = input_data.get('params')
        tool_name = params['name']
        args = params.get('arguments', {})
        break
    except Exception as ex:
        continue

if tool_name == "list_mp3s":
    MP3_DIR = Path(args.get('path') or '.').expanduser()
    mp3s = [f.name for f in MP3_DIR.rglob("*.mp3")]
    print(json.dumps(mp3s))

elif tool_name == "play_mp3":
    filename = args['filename']
    subprocess.Popen(['mpv', '--quiet', Path(args.get('path') or '.').expanduser() / filename])
    print(json.dumps({"status": "playing", "file": filename}))

else:
    print(json.dumps({"error": f"Unknown tool: {tool_name}"}))
    sys.exit(1)
