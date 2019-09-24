#!/bin/bash

run=0
download=1
sort='-week'
num='5'
script="$(dirname $0)/beatmap_link.py"
helper='node osu-replay-downloader/fetch.js'

while [ $# -gt 0 ]; do
     case "$1" in
     -hot | -hour | -day | -week | -month | -year | -all)
          sort="$1"
          ;;
     -[0-9])
          num="$1"
          ;;
     -run)
          run=1
          ;;
     -no-download)
          helper="echo 'no download'"
          ;;
     -*)
          echo invalid option: "$1"
          ;;
     esac
     shift
done
sort=$(echo "$sort" | tr -d -)
num=$(echo "$num" | tr -d -)
num_check=$((2 * $num + 1))
echo launching script "$script" with options "$helper" "$num_check" "$num" "$sort"

python "$script" "$helper" "$num_check" "$num" "$sort" || exit 1
files=""
for file in $(
     find $(pwd)/responses/downloads/ -type f -iname '*.osz'
     find $(pwd)/responses/downloads/ -type f -iname '*.osr'
); do
     echo file="$file"
     files="$files $file"
done
# echo files="$files"
#source creds/LD_LIBRARY_PATH
#source creds/osu_path

if [ $run == 1 ]; then
     #$osu_path
     export LD_LIBRARY_PATH="$(<creds/LD_LIBRARY_PATH)"
     $(<creds/osu_path) $files
     # sleep 5s; obs --start-recording &
else; 
     echo 'Skipping launching osu!'
fi
