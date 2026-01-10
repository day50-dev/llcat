# /usr/bin/cat for LLMs
**llcat** is like cURL or cat for LLMS: a stateless, low-level, idempotent composable tool for scripting and glue.

Conversations, keys, and servers are specified using classic unix patterns. Nothing is hidden or tucked away.

<img width="670" height="592" alt="llcat" src="https://github.com/user-attachments/assets/0fac2db4-3b2e-4639-b6b1-1b0a121a5744" />

## Very Quick Start
Got 0.3 seconds to spare?

List the models on [OpenRouter](https://openrouter.ai):

`uvx llcat -s https://openrouter.ai/api -m`

Run that right now. 

I'll wait.

----

llcat can:

 * Use local or remote servers, authenticated or not.
 * Store **conversation history** optionally, as a boring JSON file. 
 * Pipe things from stdin and/or be prompted on the command line.
 * Do **tool calling** using the OpenAI spec. There's an example in this repository (and below).
 * List **models** using `-m` without arguments. Specify a model with the argument.

## Examples

Start a chat with llama:
```
$ llcat -s https://openrouter.ai/api \
        -m meta-llama/llama-3.2-3b-instruct:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "What is the capital of France?"
```

Continue with Qwen:
```
$ llcat -s https://openrouter.ai/api \
        -m qwen/qwen3-4b:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "And what about Canada?"
```

And finish on the local network:
```
$ llcat -s http://192.168.1.21:8080 \
        -c /tmp/convo.txt \
        "And what about Japan?"
```
One conversation, hopping across models and servers.

## Summon Some More

The design decisions mean lots of things are within reach.

Here's one way [you could store state](https://github.com/day50-dev/llcat/blob/main/examples/state.sh):

```shell
llc()        { llcat -m "$LLC_MODEL" -s "$LLC_SERVER" -k "$LLC_KEY" "$@" }
llc-model()  { LLC_MODEL=$(llcat -m  -s "$LLC_SERVER" -k "$LLC_KEY" | fzf) }
llc-server() { LLC_SERVER=$1 }
llc-key()    { LLC_KEY=$1 }
```

And now you can do things like this:
```
$ llc-server http://192.168.1.21:8080
$ llc "write a diss track where the knapsack problem hates on the towers of hanoi"
```

## Conversant Conversations?

A conversation interface is [also quite quick](https://github.com/day50-dev/llcat/blob/main/examples/conversation.sh):

```shell
#!/bin/bash
conv=${CONV:-$(mktemp)}
echo -e "  Using: $conv\n"
jq -r '.[] | "\n**\(.role)**: \(.content)"' $conv | sd
while read -E -p "  >> " query; do
    llcat -c $conv "$@" "$query" |& sd
    echo
done
```

<img width="1918" height="1106" alt="2026-01-09_07-35" src="https://github.com/user-attachments/assets/e6584f6d-65f3-4dc8-83c7-1d2fe2b32bb0" />

## The Tool Call To Rule Them All
This example, a very strange way to play mp3s, uses the [sophisticated 21 line `tool_program.py`](https://github.com/day50-dev/llcat/blob/main/examples/tool_program.py) included in this repository. Some people call it MCP, `llcat` calls it `subprocess.run`.

This demo also uses DA`/50's pretty little [streaming markdown renderer, streamdown](https://github.com/day50-dev/Streamdown).

<img width="1919" height="606" alt="tc" src="https://github.com/user-attachments/assets/a704ae5c-cfcb-4abc-b1a7-ad1290e60510" />

There you go. Alright **a16z** where's my $50 million? 


### Formal Documentation

```shell
usage: llcat  [-h] [-c CONVERSATION] [-m [MODEL]] [-k KEY] [-s SERVER]
              [-p PROMPT] [-tf TOOL_FILE] [-tp TOOL_PROGRAM] [-a ATTACH]
              [user_prompt ...]

positional arguments:
  user_prompt           Your prompt

options:
  -h, --help            show this help message and exit
  -c, --conversation CONVERSATION
                        Conversation history file
  -m, --model [MODEL]   Model to use (or list models if no value)
  -k, --key KEY         API key for authorization
  -s, --server SERVER   Server URL (e.g., http://::1:8080)
  -p, --prompt PROMPT   System prompt
  -tf, --tool_file TOOL_FILE
                        JSON file with tool definitions
  -tp, --tool_program TOOL_PROGRAM
                        Program to execute tool calls
  -a, --attach ATTACH   Attach file(s)
```

Now it's your turn.

----

Brought to you by **DA`/50**: Make the future obvious.
