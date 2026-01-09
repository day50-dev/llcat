# /usr/bin/cat for LLMs
**llcat** is an LLM program with very little ambition. 

That's why it's awesome.

<img width="670" height="592" alt="llcat" src="https://github.com/user-attachments/assets/0fac2db4-3b2e-4639-b6b1-1b0a121a5744" />

You can handle this! 

## Very Quick Start
Got 0.3 seconds to spare?

List the models on [OpenRouter](https://openrouter.ai):

`uvx llcat -s https://openrouter.ai/api -m`

Run that right now. 

I'll wait.

----

**llcat** solves all your problems. 

Yes. Even that one.

It can also:

 * Pipe things from stdin and/or be prompted on the command line.
 * Store **conversation history** optionally, as a boring JSON file. 
 * Do **tool calling** using the OpenAI spec. There's an example in this repository (and below).
 * Use local or remote servers, authenticated or not.
 * List **models** using `-m` without arguments. Specify a model with the argument.

Free Samples? Sure! It's Free Software.

 * pipx install llcat
 * uvx llcat

Dependencies? Just the requests library.

*Note: It's **llcat**, not **llmcat**. Let's keep it pronounceable.*

## Examples

Start with llama:
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

Pure sorcery.

## Summon Some More

Want to store state? Let's go!
```shell
$ source examples/fancy.sh
$ llc-server http://192.168.1.21:8080
$ llc "write a diss track where the knapsack problem hates on the towers of hanoi"
```
Now go [read the four lines of `fancy.sh`](https://github.com/day50-dev/llcat/blob/main/examples/fancy.sh)

Surprise! Environment variables and a wrapper function. That's all you need.


## The Tool Call To Rule Them All
This example, a very strange way to play mp3s, uses the [sophisticated 21 line `example_tool_program.py`](https://github.com/day50-dev/llcat/blob/main/examples/tool_program.py) included in this repository.

It also uses DA`/50's pretty little [streaming markdown renderer, streamdown](https://github.com/day50-dev/Streamdown).

<img width="1919" height="606" alt="tc" src="https://github.com/user-attachments/assets/a704ae5c-cfcb-4abc-b1a7-ad1290e60510" />

[Kablam!](https://frustratedfunk.bandcamp.com/track/photographic-photogenic) Alright **a16z** where's my $50 million? 

The enterprise applications are limitless...

## Conversant Conversations?

Sure! [Conversation.sh is six lines of bash](https://github.com/day50-dev/llcat/blob/main/examples/conversation.sh). 

It even has inspectable tool calls and realtime observability with Human-in-the-Loop! Wowza! I'll settle for merely $40 million.

<img width="1918" height="1106" alt="2026-01-09_07-35" src="https://github.com/user-attachments/assets/e6584f6d-65f3-4dc8-83c7-1d2fe2b32bb0" />


### Boring Documentation

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

Now it's your turn.

----

Brought to you by **DA`/50**: Make the future obvious.
