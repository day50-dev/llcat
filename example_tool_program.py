#!/usr/bin/env python3
import json, sys, os, subprocess
from pathlib import Path

input_data = json.loads(sys.stdin.read())
tool_name = input_data['name']
args = input_data.get('arguments', {})

if tool_name == "list_mp3s":
    MP3_DIR = Path(args.get('path') or '.').expanduser()
    mp3s = [f.name for f in MP3_DIR.rglob("*.mp3")]
    print(json.dumps(mp3s))

elif tool_name == "play_mp3":
    filename = args['filename']
    subprocess.Popen(['mpv', filanem])
    print(json.dumps({"status": "playing", "file": filename}))

else:
    print(json.dumps({"error": f"Unknown tool: {tool_name}"}))
    sys.exit(1)
