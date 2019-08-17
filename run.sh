
python beatmap_link.py
files=""
for file in $(find "$(pwd)/responses/downloads" -type f); do
   echo file="$file"
	files="$files $file"
done
echo files="$files"
#source creds/LD_LIBRARY_PATH
#source creds/osu_path

#$osu_path
   lib_path="$(< creds/LD_LIBRARY_PATH)"
   osu_args="$(< creds/osu_path ) $files"
   LD_LIBRARY_PATH="$lib_path" $osu_args
    # sleep 5s; obs --start-recording &
