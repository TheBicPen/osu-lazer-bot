rec_folder="$(cat creds/recording_folder)"
file_to_upload="$(ls $rec_folder -t -p | grep -v / | head -n 1)"
full_path="$rec_folder/$file_to_upload"
echo "$file_to_upload"


if ! type "python" > /dev/null; then
	echo "Activating python env.."
	. "./env/bin/activate"
fi

python upload_youtube.py --file="$full_path" --description="
osu!lazer displays replays differently than stable, so there may be extra 100s/50s/misses shown. 
The score screen at the end is correct." --category=20 --title="$file_to_upload" && mv "$full_path" "$rec_folder/done/$file_to_upload" -v
