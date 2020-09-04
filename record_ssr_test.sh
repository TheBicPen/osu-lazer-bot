PIPE="/tmp/ssr-command-pipe"
mkfifo "$PIPE"
simplescreenrecorder --start-recording < "$PIPE" &
exec 4> "$PIPE"
sleep 10
echo "record-cancel" >&4
sleep 10
echo "record-start" >&4
sleep 10
echo "record-save" >&4
sleep 3
echo "quit" >&4
exec 4>&-
rm "$PIPE"
