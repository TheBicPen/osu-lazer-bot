
import beatmap_link
import subprocess
from fetch_plays import get_safe_name
from time import time, sleep
import upload_youtube
from collections import namedtuple
import os.path
from typing import List

NUM_PLAYS_CHECKED = 8
SORT_TYPE = "hot"
DOWNLOAD_OPTION = "beatmaps replays"
# REPLAY_DOWNLOAD_SCRIPT = "node osu-replay-downloader/fetch.js"
BEATMAP_LOAD_TIMEOUT = 10
MAX_REPLAY_LENGTH = 900
COMPRESSION_CRF = 5


def main():
    with open("creds/recording_folder.txt", "r") as f:
        recording_folder = f.read().strip().rstrip("/") + "/"
    replay_recordings = beatmap_link.download_plays(
        DOWNLOAD_OPTION, NUM_PLAYS_CHECKED, SORT_TYPE)

    num_imported_maps = import_maps(replay_recordings)
    print(f"Imported {num_imported_maps} maps")

    for replay_info in replay_recordings:
        if replay_info.replay_file and replay_info.play.length:
            output_file = recording_folder + get_safe_name(
                f"{replay_info.play.beatmap_name}_{replay_info.play.player_name}_{int(time())}") + ".mkv"
            print(f"Recording {replay_info.play.post_title}")
            record_ssr(replay_info.play.length+15,
                       output_file, replay_info.replay_file)
            sleep(1)
        else:
            print(f"Skipping recording of '{replay_info.play.player_name}' on map '{replay_info.play.beatmap_name}'" +
                  f"because either replay file '{replay_info.replay_file}' or play length '{replay_info.play.length}' are undefined")


def record_ffmpeg(play_length: int, output_file: str, replay_file: str):
    print("launching ffmpeg recording script with", replay_file)
    res = subprocess.run(["sh", "record_ffmpeg.sh", str(
        play_length), output_file, replay_file])
    return res.returncode


def import_maps(plays: List[beatmap_link.ReplayRecording], timeout: int = BEATMAP_LOAD_TIMEOUT) -> int:
    """
    Import beatmaps in plays. Wait 'timeout' seconds after launch before killing osu! process.
    Return number of beatmaps imported.
    """
    osu_command = ""
    with open("creds/osu_path.txt", "r") as f:
        osu_command = f.read().strip()
    maps = [play.beatmap_file for play in plays if play.beatmap_file]
    try:
        print("Launching osu! with beatmaps")
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
                                 ], stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, bufsize=0)
        try:
            sleep(3)
            proc.stdin.write(b"record-cancel\n")
            sleep(3)
            print("Starting recording")
            proc.stdin.write(b"record-start\n")
            sleep(play_length)
            proc.stdin.write(b"record-save\n")
            sleep(3)
            proc.stdin.write(b"quit\n")
            if code := proc.wait(timeout=10) != 0:
                print("SSR exited with non-0 return code:", code)
        except subprocess.TimeoutExpired:
            print("Process timed out")
    finally:
        os.remove(settings_file)
        subprocess.run(["pkill", "osu\!"])


def record(play: beatmap_link.ReplayRecording, recording_folder: str):
    output_file = recording_folder + get_safe_name(
        f"{play.beatmap_name}_{play.player_name}_{int(time())}") + ".mkv"
    # record_ffmpeg(play.length+15, output_file, play.replay_file)
    record_ssr(play.length+15, output_file, play.replay_file)
    upscaled_filename = os.path.splitext(output_file)[
        0] + "_upscaled" + os.path.splitext(output_file)[1]
    subprocess.run(["sh", "upscale.sh", str(COMPRESSION_CRF),
                    output_file, upscaled_filename])
    # upload(upscaled_filename)


def upload(file_name):
    youtube = upload_youtube.get_authenticated_service(args=None)
    # too lazy to make a class so I'm using a mock
    Args = namedtuple('args', ["file", "keywords", "title",
                               "description", "category", "privacyStatus"])
    args = Args(file_name, "keyword", "test title",
                "description", "22", "private")
    upload_youtube.initialize_upload(youtube, args)


if __name__ == "__main__":
    main()
