#!/bin/sh

SLEEP_ON_LAUNCH=5

TIME_TO_SLEEP=$1
OUTPUT_FILE=$2
REPLAY_FILE=$3
BEATMAP_FILE=$4

$(cat creds/osu_path.txt) "$REPLAY_FILE" "$BEATMAP_FILE" &    # fork osu process
OSU_PID=$!
echo "osu process ID: $OSU_PID"
sleep $SLEEP_ON_LAUNCH

# move to top left corner for screen region recording
wmctrl -r 'osu!lazer' -e 0,0,0,1280,720
wmctrl -a 'osu!lazer'
# wmctrl -r 'osu!lazer' -e 0,-1,-1,1280,720 # keep location - only for window recording
ffmpeg -video_size 1280x720 -framerate 60 -f x11grab -i :0.0 -f pulse -ac 2 -i default "$OUTPUT_FILE" &
FFMPEG_PID=$!

echo "Replay should now be loaded. Sleeping for $TIME_TO_SLEEP seconds"
sleep $TIME_TO_SLEEP

# increasingly strict process ending
wmctrl -c 'osu!lazer'
sleep 1
wmctrl -c 'osu!lazer'
kill -INT $FFMPEG_PID
if [ ! -z $(ps -p "$OSU_PID") ]; then
    kill $OSU_PID
fi
