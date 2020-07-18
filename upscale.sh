#!/bin/sh

if [ -n "$1" ]
then IN_FILE="$1"
else 
    REC_FOLDER="$(cat creds/recording_folder.txt)"
    IN_FILE="${REC_FOLDER}/$(ls $REC_FOLDER -t -p | grep -v / | head -n 1)" # get latest file
fi

AddBaseName () {
    # append suffix $2 to basename of $1

    echo "${1%.*}$2.${1##*.}" # split on last . in filename
    # echo "${1%%.*}$2.${1#*.}" # split on first . in filename
}

OUT_FILE="${2:-$(AddBaseName $IN_FILE _upscaled)}"
LOSS="${3:-0}"

echo "Upscaling $IN_FILE to $OUT_FILE with quality loss $LOSS"

ffmpeg -i "$IN_FILE" -vf scale=iw*2:ih*2 -crf "$LOSS" "$OUT_FILE"