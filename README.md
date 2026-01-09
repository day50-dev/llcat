# /usr/bin/cat for LLMs
<img width="670" height="592" alt="llcat" src="https://github.com/user-attachments/assets/0fac2db4-3b2e-4639-b6b1-1b0a121a5744" />

**llcat** is an llm program with very little ambition, and that's what makes it useful. 
There's a lot of tricked out bling cli tools out there with things like plugin systems and databases but what about the `/usr/bin/cat`?

 * You can pipe things into it or prompt it on the command line.
 * **Conversation history** is just a file you can optionally provide. If you don't then there's no conversation saved.
 * **Tool Calling** is done by using the toolcalling OpenAI spec. There's a file and a progrma example
 * 3rd party services & local: 
    * `OPENAI_API_BASE` and `LLM_BASE_URL` are supported along with -s for one off
    * **Authentication tokens** are passed with -k. You can do `$(< somefile)` or whatever obfuscation you want, that's on you.
 * **Models** can be listed with the `-m` option unadorned. Add the name and there you go.

Here's some things you can do

 * pipx install llcat
 * uv tool run llcat

## Examples

**Start with Openrouter**

Listing the models on openrouter

`llmcat -s https://openrouter.ai/api -m`

Choosing one that doing a basic query:

```
$ llcat -s https://openrouter.ai/api \
        -m meta-llama/llama-3.2-3b-instruct:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "What is the capital of France?"

$ llcat -s https://openrouter.ai/api \
        -m meta-llama/llama-3.2-3b-instruct:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "And what about Canada?"
```

**Let's continue it locally**

```
$ llcat -s http://192.168.1.21:8080 \
        -c /tmp/convo.txt \
        "And what about Japan?"
```

## Full documentation

```shell
usage: llcat [-h] [-c CONVERSATION] [-m [MODEL]] [-k KEY] [-s SERVER]
                [-tf TOOL_FILE] [-tp TOOL_PROGRAM]
                [prompt ...]

positional arguments:
  prompt                Your prompt

options:
  -h, --help            show this help message and exit
  -c, --conversation CONVERSATION
                        Conversation history file
  -m, --model [MODEL]   Model to use (or list models if no value)
  -k, --key KEY         API key for authorization
  -s, --server SERVER   Server URL (e.g., http://::1:8080)
  -tf, --tool_file TOOL_FILE
                        JSON file with tool definitions
  -tp, --tool_program TOOL_PROGRAM
                        Program to execute tool calls

```
