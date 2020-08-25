#!/bin/sh

SLEEP_ON_LAUNCH=5
CRF=6
REPLAY_LENGTH=$1
OUTPUT_FILE=$2
REPLAY_FILE=$3

pkill 'osu!'
$(cat creds/osu_path.txt) $REPLAY_FILE &    # fork osu process
OSU_PID=$!
echo "osu process ID: $OSU_PID"
sleep $SLEEP_ON_LAUNCH

# move to top left corner for screen region recording
wmctrl -r 'osu!lazer' -e 0,-2,-30,1280,720 # adjust for window border
wmctrl -a 'osu!lazer'
# wmctrl -r 'osu!lazer' -e 0,-1,-1,1280,720 # keep location - only for window recording

echo "Replay should now be loaded. Recording for $REPLAY_LENGTH seconds"

# echo "Checking for osu!lazer window"
# until [ $(wmctrl -p -l | grep osu!lazer | grep $OSU_PID) ]; do
# sleep 0.5
# echo "Waiting for osu!lazer window to appear"
# done


ffmpeg -video_size 1280x720 -framerate 60 -f x11grab -i :0.0 -f pulse -ac 2 -i default -crf "$CRF" -t "$REPLAY_LENGTH" "$OUTPUT_FILE"
kill $OSU_PID
# # increasingly strict process ending
# wmctrl -c 'osu!lazer'
# sleep 1
# wmctrl -c 'osu!lazer'
# sleep 1
# if [ ! -z "$(ps -p "$OSU_PID")" ]; then
#     kill $OSU_PID
# fi
