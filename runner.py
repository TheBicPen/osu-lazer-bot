
import download
import subprocess
import fetch_plays as fp
from time import time, sleep
import upload_youtube
from collections import namedtuple
import os.path
from typing import List
import sys

NUM_POSTS_CHECKED = 8
SORT_TYPE = "hot"
DOWNLOAD_OPTION = "beatmaps replays"
BEATMAP_LOAD_TIMEOUT = 10
MAX_REPLAY_LENGTH = 900
COMPRESSION_CRF = 5
MODE="auto"


def main(mode: str, num_plays: int, sort_type: str):


    if mode in ["auto", "interactive"]:
        replay_infos = download.download_plays(
            DOWNLOAD_OPTION, num_plays, sort_type)
    elif mode in ["manual"]:
        manual()
        return

    num_imported_maps = import_maps(replay_infos)
    print(f"Imported {num_imported_maps} maps")

    for replay_info in replay_infos:
        if replay_info.replay_file and replay_info.play.length:
            record(replay_info)
            print("Upscaling file")
            upscale(replay_info)
            print("Uploading file")
            upload(replay_info)
            sleep(3)
        else:
            print(f"Skipping recording '{replay_info.play.player_name} - {replay_info.play.beatmap_name}'" +
                  f"because either replay file '{replay_info.replay_file}' or play length '{replay_info.play.length}' are missing")


def manual():
    reddit = fp.initialize()
    recording = None
    action = "add"
    while action != "exit":
        try:
            if action == "add":
                post_id = input("Please input a post ID: ")
                post = fp.get_scorepost_by_id(post_id, reddit)
                recording = download.ReplayRecording(post)
            elif action == "download":
                if input("Download replays? [y/n]: ") == "y":
                    download.download_replays([recording])
                if input("Download beatmaps? [y/n]: ") == "y":
                    download.download_beatmapsets([recording])
            elif action == "set":
                prop = input("Property name to set: ")
                obj_to_set = recording
                try:
                    for i in prop.split(".")[:-1]:
                        obj_to_set = getattr(obj_to_set, i)
                    prop_name = prop.split(".")[-1]
                    print(f"Current value of property {prop_name}: {getattr(obj_to_set, prop_name)}")
                    value = input("Property value to set: ")
                    setattr(obj_to_set, prop_name, value)
                except AttributeError:
                    print(f"Recording {obj_to_set} has no property named {prop}. See {dir(obj_to_set)}")
            elif action == "go":
                num_imported_maps = import_maps([recording])
                print(f"Imported {num_imported_maps} maps")
                record(recording)
                factor = int(input("Select compression ratio [0-25]"))
                upscale(recording, compression=factor)
                upload(recording)
        except KeyboardInterrupt as e:
            print()
        finally:
            print("Score:", recording)
            action = input("Menu:\n\t[set] property of recording\n\t[download] replays and beatmaps\n\t[add] post\n\t[go] record and upload scores\n\t[exit]\n")


def record_ffmpeg(play_length: int, output_file: str, replay_file: str):
    print("Launching ffmpeg recording script with", replay_file)
    res = subprocess.run(["sh", "record_ffmpeg.sh", str(
        play_length), output_file, replay_file])
    return res.returncode


def import_maps(plays: List[download.ReplayRecording], timeout: int = BEATMAP_LOAD_TIMEOUT) -> int:
    """
    Import beatmaps in plays. Wait 'timeout' seconds after launch before killing osu! process.
    Return number of beatmaps imported.
    """
    with open("creds/osu_path.txt", "r") as f:
        osu_command = f.read().strip()
    maps = [play.beatmap_file for play in plays if play.beatmap_file]
    if len(maps) == 0:
        print("No maps to import!")
        return
    try:
        print("Importing beatmaps")
        subprocess.run([osu_command, *maps], timeout=timeout)
    except subprocess.TimeoutExpired:
        print("Killing osu!")
    return len(maps)


def record_ssr(play_length: int, output_file: str, replay_file: str):
    print(f"Recording with SSR for {play_length} seconds")
    # this will launch osu but fail to record since the startup takes time
    settings_template = "creds/settings.conf"
    settings_file = os.path.realpath("settingsfile.conf")
    try:
        with open(settings_template, "r") as r, open(settings_file, "w+") as w:
            w.write(r.read()
                    .replace("$REPLAY_FILE", replay_file)
                    .replace("$OUTPUT_FILE", output_file))
        proc = subprocess.Popen(["simplescreenrecorder",
                                 # "--start-hidden",
                                 "--start-recording",
                                 "--settingsfile=" + settings_file
                                 ], stdin=subprocess.PIPE, bufsize=0)

        sleep(3)
        proc.stdin.write(b"record-cancel\n")
        sleep(3)
        print("Starting recording")
        # try recording several times
        proc.stdin.write(b"record-start\n")
        sleep(1)
        proc.stdin.write(b"record-start\n")
        sleep(1)
        proc.stdin.write(b"record-start\n")
        sleep(play_length)
        proc.stdin.write(b"record-save\n")
        sleep(3)
        proc.stdin.write(b"quit\n")
        if code := proc.wait(timeout=10) != 0:
            print("SSR exited with non-0 return code:", code)
    except subprocess.TimeoutExpired:
        print("SSR process timed out")
    finally:
        os.remove(settings_file)
        subprocess.run(["pkill", "osu\!"])


def record(replay_info: download.ReplayRecording, recording_folder: str = None):
    if recording_folder is None:
        with open("creds/recording_folder.txt", "r") as f:
            recording_folder = f.read()
    output_file = os.path.join(recording_folder, fp.get_safe_name(
        f"{replay_info.play.beatmap_name}_{replay_info.play.player_name}_{int(time())}") + ".mkv")
    record_ssr(replay_info.play.length+15,
               output_file, replay_info.replay_file)
    replay_info.video_file = output_file
    return output_file


def upscale(play: download.ReplayRecording, infile: str = None, outfile: str = None, compression: int = COMPRESSION_CRF):
    if infile is None:
        infile = play.video_file
    if outfile is None:
        outfile = os.path.splitext(
            infile)[0] + "_upscaled" + os.path.splitext(infile)[1]
    subprocess.run(["sh", "upscale.sh", str(
        compression), infile, outfile], check=True)
    play.video_file = outfile
    return outfile


def upload(play: download.ReplayRecording):
    youtube = upload_youtube.get_authenticated_service(args=None)
    play.generate_video_attributes()
    # too lazy to make a class so I'm using a mock
    Args = namedtuple('args', ["file", "keywords", "title",
                               "description", "category", "privacyStatus"])
    args = Args(play.video_file, play.video_tags, play.video_title,
                play.video_description, play.video_category, "private")
    print("Uploading video: ", args)
    return upload_youtube.initialize_upload(youtube, args)


if __name__ == "__main__":
    for arg in sys.argv:
        if arg in ["interactive", "auto", "manual"]:
            MODE=arg
        elif arg in ["hot", "hour", "day", "week", "month", "year", "all"]:
            SORT_TYPE = arg
        elif arg.isdigit():
            NUM_POSTS_CHECKED = int(arg)
    main(mode=MODE, sort_type=SORT_TYPE, num_plays=NUM_POSTS_CHECKED)
