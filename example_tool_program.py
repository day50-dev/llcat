#!/usr/bin/env python3
import json
import sys
import os
import subprocess
from pathlib import Path

# Read input
input_data = json.loads(sys.stdin.read())
tool_name = input_data['name']
args = input_data.get('arguments', {})
MP3_DIR = Path.cwd()

if tool_name == "list_mp3s":
    # List all MP3 files
    mp3s = [f.name for f in MP3_DIR.rglob("*.mp3")]
    print(json.dumps(mp3s))

elif tool_name == "play_mp3":
    filename = args['filename']
    
    # Find the file
    matches = list(MP3_DIR.rglob(filename))
    
    if not matches:
        print(json.dumps({"error": f"File not found: {filename}"}))
        sys.exit(1)
    
    filepath = matches[0]
    
    # Play the file (afplay on macOS, adjust for your system)
    subprocess.Popen(['mpv', str(filepath)])
    
    print(json.dumps({"status": "playing", "file": filename}))

else:
    print(json.dumps({"error": f"Unknown tool: {tool_name}"}))
    sys.exit(1)
