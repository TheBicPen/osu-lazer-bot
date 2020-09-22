#!/bin/bash

run=0
download='replays beatmaps'
sort='-hot'
num_check='8'
helper='node osu-replay-downloader/fetch.js'

while [ $# -gt 0 ]; do
     case "$1" in
     -hot | -hour | -day | -week | -month | -year | -all)
          sort="$1"
          ;;
     -[0-9])
          num_check="$1"
          ;;
     -run)
          run=1
          ;;
     -beatmaps)
          download='beatmaps'
          ;;
     -replays)
          download='replays'
          ;;
     -none)
          download=''
          ;;
     -download-all)
          download='beatmaps replays'
          ;;
     -*)
          echo invalid option: "$1"
          ;;
     esac
     shift
done

# remove '-' prefixes
sort=$(echo "$sort" | tr -d -)
num_check=$(echo "$num_check" | tr -d -)

cd "$(dirname $0)"
. "./env/bin/activate"

python download.py "$download" "$helper" "$num_check" "$sort" || exit 1
files=""
for file in $(
     find $(pwd)/downloads/ -type f -iname '*.osz'
     find $(pwd)/downloads/ -type f -iname '*.osr'
); do
     echo file="$file"
     files="$files $file"
done

if [ $run = 1 ]; then
     $(<creds/osu_path) $files
else 
     echo 'Skipping launching osu!'
fi
