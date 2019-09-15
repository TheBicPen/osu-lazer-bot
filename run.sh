#!/bin/bash

sort='-week'
num='5'
while [ $# -gt 0 ]; do
    case "$1" in
    -hot | -hour | -day | -week | -month | -year | -all)
         sort="$1"
         ;;
    -[0-9])
         num="$1"
         ;;
    -*)
        echo invalid option: "$1"
        ;;
    esac
    shift
done
sort=$(echo "$sort" | tr -d -)
num=$(echo "$num" | tr -d -)
script="$(dirname $0)/beatmap_link.py"
helper='node osu-replay-downloader/fetch.js'
echo launching script "$script" with options $helper "$num" "$sort"

python "$script" $helper "$num" "$sort" || exit 1
files=""
for file in $(find $(pwd)/responses/downloads/ -type f -iname '*.osz' ; find $(pwd)/responses/downloads/ -type f -iname '*.osr'); do
   echo file="$file"
	files="$files $file"
done
# echo files="$files"
#source creds/LD_LIBRARY_PATH
#source creds/osu_path

#$osu_path
   export LD_LIBRARY_PATH="$(< creds/LD_LIBRARY_PATH)"
   $(< creds/osu_path) $files
    # sleep 5s; obs --start-recording &
