
python beatmap_link.py
files=""
for file in $(find "$(pwd)/responses/downloads" -type f); do
	files="$files $file"
done
echo $files
source creds/LD_LIBRARY_PATH
source creds/osu_path

$osu_path
   # LD_LIBRARY_PATH=$(cat creds/LD_LIBRARY_PATH) $(cat creds/osu_path) file
    # sleep 5s; obs --start-recording &
