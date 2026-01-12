<p align="center">
<img width="238" alt="llcat" src="https://github.com/user-attachments/assets/c161862d-8a8e-4753-a6eb-8a3b67f760b0" />
<br/> <strong>/usr/bin/cat for LLMs</h3></strong>
</p>
<hr>

**llcat** is a general-purpose CLI-based OpenAI-compatible `/chat/completions` caller. 

It is like cURL or cat for LLMs: a stateless, transparent, explicit, low-level, composable tool for scripting and glue.

Conversations, keys, servers and other configurations are explicitly specified each execution as command line arguments. 
This makes building things with llcat simple and direct.

There is no caching or state saved between runs. Everything gets surfaced and errors are JSON parsable.

## Very Quick Start
Got 0.3 seconds to spare?

List the models on [OpenRouter](https://openrouter.ai):

`uvx llcat -u https://openrouter.ai/api -m`

----

**llcat** can:

 * Use local or remote servers, authenticated or not.
 * Store **conversation history** optionally, as a JSON file. 
 * Pipe things from stdin and/or be prompted on the command line.
 * Do **tool calling** using the OpenAI spec and MCP STDIO servers.
 * List and choose models, system prompts, and add attachments.

llcat's basic CLI parameters are also compatible with [Simon Willison's llm](https://github.com/simonw/llm).

## Example: Transferrable Conversations

Because conversations, models and servers are decoupled, you can easily mix and match them at any time.

Here's one conversation, hopping across models and servers.

Start a chat with Deepseek:
```
$ llcat -u https://openrouter.ai/api \
        -m deepseek/deepseek-r1-0528:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "What is the capital of France?"
```

Continue it with Qwen:
```
$ llcat -u https://openrouter.ai/api \
        -m qwen/qwen3-4b:free \
        -c /tmp/convo.txt \
        -k $(cat openrouter.key) \
        "And what about Canada?"
```

And finish on the local network:
```
$ llcat -u http://192.168.1.21:8080 \
        -c /tmp/convo.txt \
        "And what about Japan?"
```

Since the conversation goes to the filesystem as easily parsable JSON  you can use things like `inotify` or `fuse` and push it off to a vector search backend or modify the context window between calls.
 
## Example: Adding State

**llcat's** explicit syntax means lots of things are within reach.

For instance simple wrappers can be made custom to your workflow. 

Here's a way [to store state](https://github.com/day50-dev/llcat/blob/main/examples/state.sh) with environment variables to make invocation more convenient:

```shell
llc()        { llcat -m "$LLC_MODEL" -u "$LLC_SERVER" -k "$LLC_KEY" "$@" }
llc-model()  { LLC_MODEL=$(llcat -m  -s "$LLC_SERVER" -k "$LLC_KEY" | fzf) }
llc-server() { LLC_SERVER=$1 }
llc-key()    { LLC_KEY=$1 }
```

And now you can do things like this:
```
$ llc-server http://192.168.1.21:8080
$ llc "write a diss track where the knapsack problem hates on the towers of hanoi"
```

There's no configuration files to parse or implicit states to manage.

## Example: Interactive Chat

A conversation interface is [also quite quick](https://github.com/day50-dev/llcat/blob/main/examples/conversation.sh):

```shell
#!/usr/bin/env bash
conv=${CONV:-$(mktemp)}
echo -e "  Using: $conv\n"
jq -r '.[] | "\n**\(.role)**: \(.content)"' $conv | sd
while read -E -p "  >> " query; do
    llcat -c $conv "$@" "$query" |& sd
    echo
done
```

<img width="1918" height="1106" alt="2026-01-09_07-35" src="https://github.com/user-attachments/assets/e6584f6d-65f3-4dc8-83c7-1d2fe2b32bb0" />

## Example: Evals
Running the same thing on multiple models and assessing the outcome is straight forward. Here we're using [ollama](https://ollama.com)

```script
pre="llcat -u http://localhost:11434"
for model in $($pre -m); do
   $pre -m $model "translate 国際化がサポートされています。to english" > ${model}.outcome
done
```

You can use patterns like that also for testing tool calling completion.

If an error happens contacting the server, you get the request, response, and exits non-zero.

## Example: Tool calling
This example, a very strange way to play mp3s, uses a [21 line `tool_program.py`](https://github.com/day50-dev/llcat/blob/main/examples/tool_program.py) included in this repository. 

<img width="1919" height="606" alt="tc" src="https://github.com/user-attachments/assets/a704ae5c-cfcb-4abc-b1a7-ad1290e60510" />


In this example you can see how nothing is hidden so when the LLM made the mistake it was immediately identifiable. 

That meta information goes to `stderr`.

llcat's tool calling is also MCP compatible.


## Usage

Now it's your turn. 

```shell
usage: llcat [-h] [-c CONVERSATION] [-m [MODEL]] [-sk KEY] [-su SERVER]
             [-s SYSTEM] [-tf TOOL_FILE] [-tp TOOL_PROGRAM] [-a ATTACH]
             [user_prompt ...]

positional arguments:
  user_prompt           Your prompt

options:
  -h, --help            show this help message and exit
  -c, --conversation CONVERSATION
                        Conversation history file
  -m, --model [MODEL]   Model to use (or list models if no value)
  -sk, --key KEY        Server API key for authorization
  -su, -u, --server SERVER
                        Server URL (e.g., http://::1:8080)
  -s, --system SYSTEM   System prompt
  -tf, --tool_file TOOL_FILE
                        JSON file with tool definitions
  -tp, --tool_program TOOL_PROGRAM
                        Program to execute tool calls
  -a, --attach ATTACH   Attach file(s)
  --version             show program's version number and exit
```

We're excited to see what you build.

----

Brought to you by **DA`/50**: Make the future obvious.
