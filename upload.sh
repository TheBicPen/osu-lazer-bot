REC_FOLDER="$(cat creds/recording_folder.txt)"
FILE_TO_UPLOAD="$(ls $REC_FOLDER -t -p | grep -v / | head -n 1)"
FULL_PATH="$REC_FOLDER/$FILE_TO_UPLOAD"
echo "$FILE_TO_UPLOAD"


if ! type "python" > /dev/null; then
	echo "Activating python env.."
	. "./env/bin/activate"
fi

python upload_youtube.py --file="$FULL_PATH" --description="


osu!lazer displays replays differently than stable, so there may be extra 100s/50s/misses shown. 
The score screen at the end is correct." --category=20 --title="$FILE_TO_UPLOAD" && 
mv "$FULL_PATH" "$REC_FOLDER/done/$FILE_TO_UPLOAD" -v
