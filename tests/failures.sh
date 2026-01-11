#!/bin/bash

ll=$1
[[ -e /tmp/key_file ]] || touch /tmp/key_file 
chmod 000 /tmp/key_file

set -x

$ll 

$ll -s invalid_url

$ll -s http://unreachable

$ll -s http://unreachable -m

$ll -s https://openrouter.ai/api/ -m bogus_model

$ll -s https://openrouter.ai/api/ -m openai/gpt-4

$ll -s https://openrouter.ai/api/ -m openai/gpt-4 -k bogus_key

$ll -s https://openrouter.ai/api/ -m openai/gpt-4 -k /tmp/key_file
