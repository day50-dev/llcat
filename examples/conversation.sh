#!/bin/bash
conv=${CONV:-$(mktemp)}
jq -r '.[] | "**\(.role)**: \(.content)"' $conv | sd
echo $conv
while read -E -p "> " query; do 
    llcat -c $conv "$@" "$query" |& sd
    echo
done
