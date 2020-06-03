rec_folder="$(cat creds/recording_folder)"
file_to_upload="$(ls $rec_folder -t | head -n 1)"
full_path="$rec_folder/$file_to_upload"
echo "$file_to_upload"

python upload_youtube.py --file="$full_path" --description="
osu!lazer displays replays differently than stable, so there may be extra 100s/50s/misses shown. 
The score screen at the end is correct." --category=20 --title="$file_to_upload" 