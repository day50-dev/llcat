#!/bin/bash

ll=$1
[[ -e /tmp/key_file ]] || touch /tmp/key_file 
chmod 000 /tmp/key_file

set -x

$ll 

$ll -u invalid_url

$ll -u http://unreachable

$ll -u http://unreachable -m

$ll -u https://openrouter.ai/api/ -m bogus_model

$ll -u https://openrouter.ai/api/ -m openai/gpt-4

$ll -u https://openrouter.ai/api/ -m openai/gpt-4 -k bogus_key

$ll -u https://openrouter.ai/api/ -m openai/gpt-4 -k /tmp/key_file
