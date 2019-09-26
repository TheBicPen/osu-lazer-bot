#!/bin/sh

in_path=~/Videos
out_path=~/Videos/out
file=$in_path/input.mkv
out=$out_path/output.mkv

if [ $# -eq 2 ]; then
	file="$1"
	out="$2"
elif [ $# -eq 1 ]; then
	if [ "$1" == '-a' ]; then
		file=$(ls -t -p $in_path | grep -v "/$" | head -1)
		out=$out_path/$file
		file=$in_path/$file
		echo Using "$file" as the input and "$out" as the output
	else
		echo "Usage: \"\$ speed_up.sh [input_file output_file] | -a | []\""
		exit 1
	fi
else
	echo "No files provided. Assuming input = $file, output = $out"
fi

if ! [ -r $file ]; then 
	echo "Unable to read $file"
	exit 1
elif [ -e $out ]; then
	echo "$out already exists."
	exit 1
fi

ffmpeg -i "$file" -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -r 60 -map "[v]" -map "[a]" "$out"
