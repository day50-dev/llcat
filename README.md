# /usr/bin/cat for LLMs
**llcat** is an LLM program with very little ambition. 

That's why it's awesome.

<img width="670" height="592" alt="llcat" src="https://github.com/user-attachments/assets/0fac2db4-3b2e-4639-b6b1-1b0a121a5744" />

You can handle this! 

**llcat** solves all your problems. 

Yes. Every one. 

It can also:

 * Pipe things from stdin and/or be prompted on the command line.
 * Store **conversation history** optionally, in a normal file. 
 * Do **tool calling** using the OpenAI spec. There's an example in this repository (and below).
 * Use local or remote servers, authenticated or not.
 * List **models** using `-m` without arguments. Specify a model with the argument.

Free Samples? Sure! It's Free Software.

 * pipx install llcat
 * uvx llcat

It's **llcat**, not **llmcat**. Let's keep it pronounceable.

Dependencies? Just the requests library.

Pretty unambitious. Pretty nice.

## Examples

List the models on [OpenRouter](https://openrouter.ai):

`uvx llcat -s https://openrouter.ai/api -m`

Go ahead, do that one right now.

```
$ llcat -s https://openrouter.ai/api \
        -m meta-llama/llama-3.2-3b-instruct:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "What is the capital of France?"
```
Let's continue but change the model:

```
$ llcat -s https://openrouter.ai/api \
        -m qwen/qwen3-4b:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "And what about Canada?"
```

And now, the server:

```
$ llcat -s http://192.168.1.21:8080 \
        -c /tmp/convo.txt \
        "And what about Japan?"
```
One conversation, hopping across models and servers.

Pure sorcery.

Want to store state? Let's go!
```shell
$ source fancy.sh
...
$ llc "write a diss track where the knapsack problem hates on the towers of hanoi"
```
What goes in the `...`? 

You'll have to read the four lines of `fancy.sh`! 

*(Spoiler Alert: it sets environment variables and has a wrapper function)*


## The Tool Call To Rule Them All
This example, a very strange way to play mp3s, uses the sophisticated 21 line `example_tool_program.py` included in this repository.

It also uses DA`/50's pretty little [streaming markdown renderer, streamdown](https://github.com/day50-dev/Streamdown).

<img width="1919" height="606" alt="tc" src="https://github.com/user-attachments/assets/a704ae5c-cfcb-4abc-b1a7-ad1290e60510" />

[Kablam!](https://frustratedfunk.bandcamp.com/track/photographic-photogenic) Alright **a16z** where's my $50 million? 

The enterprise applications are limitless...

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
