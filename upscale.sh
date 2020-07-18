#!/bin/sh

AddBaseName () {
    # append suffix $2 to basename of $1

    echo "${1%.*}$2.${1##*.}" # split on last . in filename
    # echo "${1%%.*}$2.${1#*.}" # split on first . in filename
}

LOSS="${1:-0}"
if [ -n "$2" ]
then IN_FILE="$2"
else 
    REC_FOLDER="$(cat creds/recording_folder.txt)"
    IN_FILE="${REC_FOLDER}/$(ls $REC_FOLDER -t -p | grep -v / | head -n 1)" # get latest file
fi
OUT_FILE="${3:-$(AddBaseName $IN_FILE _upscaled)}"

echo "Upscaling $IN_FILE to $OUT_FILE with quality loss $LOSS"
ffmpeg -n -i "$IN_FILE" -vf scale=iw*2:ih*2 -crf "$LOSS" "$OUT_FILE" && echo 'ffmpeg exited without errors'