# /usr/bin/cat for LLMs
**llcat** is an LLM program with very little ambition in life. 

That's what makes it useful. 

<img width="670" height="592" alt="llcat" src="https://github.com/user-attachments/assets/0fac2db4-3b2e-4639-b6b1-1b0a121a5744" />

You can handle this! 

**llcat** solves all your problems. Yes, all of them! 

You can also:

 * Pipe things into it or prompt it on the command line.
 * **Conversation history** as an optional file. 
 * **Tool Calling** with the OpenAI spec. There's a file and a program example in this repository.
 * Servers: 
    * `OPENAI_API_BASE` and `LLM_BASE_URL` are supported along with -s for one off.
    * **Authentication tokens** are passed with -k. You can do `$(< somefile)` or whatever obfuscation you want, that's on you.
 * **Models** are listed with the `-m` option and specified with it as well.

Want it?

 * pipx install llcat
 * uv tool run llcat

Dependency? Just the requests library. That's it.

## Examples

List the models on openrouter

`llcat -s https://openrouter.ai/api -m`

Go ahead, you can run that, unauthenticated, no problem.

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

Pure sorcery.

## The Tool Call To Rule Them All
This uses the sophisticated 21 line `example_tool_program.py` included in this repository.

It also uses DA`/50's pretty little [streaming markdown renderer, streamdown](https://github.com/day50-dev/Streamdown).

<img width="1919" height="606" alt="tc" src="https://github.com/user-attachments/assets/a704ae5c-cfcb-4abc-b1a7-ad1290e60510" />

[Kablam!](https://frustratedfunk.bandcamp.com/track/photographic-photogenic) Alright **a16z** where's my $50 million? 

The enterprise applications are limitless...

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
