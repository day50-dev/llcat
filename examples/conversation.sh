#!/usr/bin/env bash
conv=${CONV:-$(mktemp)}
echo -e "  Using: $conv\n"
jq -r '.[] | "\n**\(.role)**: \(.content)"' $conv | sd
while read -E -p "  >> " query; do 
    llcat -c $conv "$@" "$query" |& sd
    echo
done
