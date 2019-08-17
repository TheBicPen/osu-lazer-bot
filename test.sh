
#source creds/LD_LIBRARY_PATH
#source creds/osu_path

#$osu_path
   LD_LIBRARY_PATH=$(cat creds/LD_LIBRARY_PATH) $(cat creds/osu_path)
    # sleep 5s; obs --start-recording &
