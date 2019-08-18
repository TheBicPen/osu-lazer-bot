

python beatmap_link.py 'node' 'osu-replay-downloader/fetch.js' 3 || exit 1
files=""
for file in $(find $(pwd)/responses/downloads/ -type f -iname '*.osz' ; find $(pwd)/responses/downloads/ -type f -iname '*.osr'); do
   echo file="$file"
	files="$files $file"
done
echo files="$files"
#source creds/LD_LIBRARY_PATH
#source creds/osu_path

#$osu_path
   export LD_LIBRARY_PATH="$(< creds/LD_LIBRARY_PATH)"
   $(< creds/osu_path) $files
    # sleep 5s; obs --start-recording &
