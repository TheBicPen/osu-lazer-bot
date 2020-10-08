
import download
import subprocess
import fetch_plays as fp
from time import time, sleep
import upload_youtube
from collections import namedtuple
import os.path
from typing import List
import sys

# default options
BEATMAP_LOAD_TIMEOUT = 10
MAX_REPLAY_LENGTH = 900
COMPRESSION_CRF = 5
MODE = "auto"
SCALE = "ffmpeg"


def main(mode: str = MODE, *args):
    """
    Mode is one of "manual", "single", "auto".
        "manual" takes no args and prompts the user for everything.
        "single" records and uploads a single replay from a reddit post.
            This mode takes the reddit post id and whether to post the replay video as args. 
        "auto" retrieves scoreposts from reddit and records them.
            This mode takes the number of posts to check and the subreddit sort type as args.
    """

    if mode == "manual":
        manual(*args)
        return
    elif mode == "single":
        single(*args)
        return

    elif mode == "auto":
        if len(args) > 1:
            replay_infos = download.download_plays(
                args[0], int(args[1]), *args[2:])
        else:
            replay_infos = download.download_plays(*args)
        num_imported_maps = import_maps(replay_infos)
        print(f"Imported {num_imported_maps} maps")

        for replay_info in replay_infos:
            make_video(replay_info)
            sleep(3)
    elif mode == "stream":
        stream(*args)
        return
    else:
        print("invalid mode", mode)


def stream(scale=SCALE):
    reddit = fp.initialize()
    for post in reddit.subreddit("osugame").stream.submissions():
        try:
            print(post.title)
            if comment := fp.get_scorepost_comment(post, "osu-bot"):
                replay_info = download.ReplayRecording(
                    fp.ScorePostInfo(comment))
                download.download_beatmapsets([replay_info])
                download.download_replays([replay_info])
                import_maps([replay_info])
                print("Recording video", replay_info)
                make_video(replay_info, scale)
        except Exception:
            pass  # ¯\_(ツ)_/¯


def single(post_id: str = None, post_to_reddit=False, scale=SCALE):
    reddit = fp.initialize()
    recording = None
    if post_id is None:
        post_id = input("Please input a post ID: ")
    post = fp.get_scorepost_by_id(post_id, reddit)
    recording = download.ReplayRecording(post)
    download.download_replays([recording])
    download.download_beatmapsets([recording])
    num_imported_maps = import_maps([recording])
    print(f"Imported {num_imported_maps} maps")
    vid_id = make_video(recording, scale)
    print("Uploaded video with id", vid_id)
    if post_to_reddit:
        posted_comment = fp.post_vid_to_reddit(vid_id, post_id, reddit)
        print("Posted comment", posted_comment)


def make_video(replay_info: download.ReplayRecording, scale: str = SCALE):
    """ 
    The video production pipeline. Records and uploads a replay from replay_info.
    Scale controls whether or not the video gets upscaled to 1440p.
        "auto" scales while recording (this results in lower performance but faster overall pipeline and smaller output file)
        "ffmpeg" scales the video after recording with compression ration COMPRESSION_CRF, defined at the top of this file.
        Other values do not upscale the video.
        Returns the video id if it was uploaded successfully.
    """
    try:
        if replay_info.replay_file and replay_info.play.length:
            if scale == "auto":
                record(replay_info, None, True)
            elif scale == "ffmpeg":
                record(replay_info, None, False)
                upscale(replay_info)
                print("Upscaled file with ffmpeg")
            return upload(replay_info)
        else:
            print(f"Skipping recording '{replay_info.play.player_name} - {replay_info.play.beatmap_name}'" +
                  f"because either replay file '{replay_info.replay_file}' or play length '{replay_info.play.length}' are missing")
            return None
    except AttributeError:
        print("replay_info has no valid play object attached")
        return None


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
            elif action == "autoset":
                action = input(
                    "Choose properties to autoset:\n\t[bc] - beatmap by comment\n\t[bu] - beatmap by url\n\t[mods]\n")
                if action == "bc":
                    try:
                        recording.play.set_beatmap(input("Comment text: "))
                    except AttributeError:
                        print("Recording has no play to set attributes of")
                elif action == "bu":
                    try:
                        success = recording.play.set_beatmap_url(input("Beatmap URL: "))
                        if not success:
                            print("URL did not match")
                    except AttributeError:
                        print("Recording has no play to set attributes of")
                elif action == "mods":
                    try:
                        recording.play.set_mods(input("Mods: "))
                    except AttributeError:
                        print("Recording has no play to set attributes of")
                        
            elif action == "set":
                prop = input("Property name to set: ")
                obj_to_set = recording
                try:
                    for i in prop.split(".")[:-1]:
                        obj_to_set = getattr(obj_to_set, i)
                    prop_name = prop.split(".")[-1]
                    print(
                        f"Current value of property {prop_name}: {getattr(obj_to_set, prop_name)}")
                    value = input("Property value to set: ")
                    setattr(obj_to_set, prop_name, value)
                    print(f"Set {prop_name} of {obj_to_set} to {value}")
                except AttributeError:
                    print(
                        f"Recording {obj_to_set} has no property named {prop}. See {dir(obj_to_set)}")
            elif action == "go":
                num_imported_maps = import_maps([recording])
                print(f"Imported {num_imported_maps} maps")
                record(recording)
                factor = int(input("Select compression ratio [0-25]"))
                upscale(recording, compression=factor)
                print("Upscaled file")
                recording.generate_video_attributes()
                print("Generated video attributes")
                vid_id = upload(recording)
                print("Uploaded video", vid_id)
        except KeyboardInterrupt:
            print("Back to main menu")
        print("Score:", recording)
        action = input(
            "Menu:\n\t[set] property of recording\n\t[autoset] properties\n\t[download] replays and beatmaps\n\t[add] post\n\t[go] record and upload scores\n\t[exit]\n")


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


def record_ssr(play_length: int, output_file: str, replay_file: str, settings_template: str = "creds/settings.conf"):
    print(f"Recording with SSR for {play_length} seconds")
    settings_file = os.path.realpath("settingsfile.conf")
    try:
        with open(settings_template, "r") as r, open(settings_file, "w+") as w:
            w.write(r.read()
                    .replace("$REPLAY_FILE", replay_file)
                    .replace("$OUTPUT_FILE", output_file))
        # this will launch osu but fail to record since the startup takes time
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


def record(replay_info: download.ReplayRecording, recording_folder: str = None, autoscale: bool = True):
    if recording_folder is None:
        with open("creds/recording_folder.txt", "r") as f:
            recording_folder = f.read()
    output_file = os.path.join(recording_folder, fp.get_safe_name(
        f"{replay_info.play.beatmap_name}_{replay_info.play.player_name}_{int(time())}") + ".mkv")
    conf_file = "creds/settings_autoscale.conf" if autoscale else "creds/settings.conf"
    record_ssr(get_recording_length(replay_info), output_file,
               replay_info.replay_file, conf_file)
    replay_info.video_file = output_file
    return output_file


def get_recording_length(replay_info: download.ReplayRecording) -> int:
    length = int(replay_info.play.length)
    return length + 10 + max(length // 30, 15)


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
    main(*sys.argv[1:])
