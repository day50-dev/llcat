#!/bin/bash
conv=$(mktemp)
echo "Welcome to cutting edge technology!"
while read -E -p "> " query; do 
    llcat -c $conv "$@" "$query" |& sd
done
