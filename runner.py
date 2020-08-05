
import beatmap_link
import subprocess
from fetch_plays import get_safe_name
from time import time
import upload_youtube
from collections import namedtuple
from os.path import splitext


NUM_PLAYS_CHECKED = 8
SORT_TYPE = "hot"
DOWNLOAD_OPTION = "beatmaps replays"
REPLAY_DOWNLOAD_SCRIPT = "node osu-replay-downloader/fetch.js"
BEATMAP_LOAD_TIMEOUT = 10
MAX_REPLAY_LENGTH = 900
COMPRESSION_CRF = 5


def main():
    osu_command = ""
    with open("creds/osu_path.txt", "r") as f:
        osu_command = f.read().strip()
    with open("creds/recording_folder.txt", "r") as f:
        recording_folder = f.read().strip().rstrip("/") + "/"
    downloads = beatmap_link.main(
        DOWNLOAD_OPTION, REPLAY_DOWNLOAD_SCRIPT, NUM_PLAYS_CHECKED, SORT_TYPE)
    if maps := downloads.get("beatmaps"):
        try:
            print("launching osu with beatmaps")
            subprocess.run([osu_command, *maps], timeout=BEATMAP_LOAD_TIMEOUT)
        except subprocess.TimeoutExpired:
            print("osu! instance killed after loading maps")
    if plays := downloads.get("plays"):
        for play_obj in plays:
            if play := check_play_obj(play_obj):
                try:
                    output_file = recording_folder + get_safe_name(
                        f"{play.beatmap_name}_{play.player_name}_{int(time())}") + ".mkv"
                    replay_file = play_obj["replay_file"]
                    print("launching recording script with", replay_file)
                    subprocess.run(
                        ["sh", "launch.sh", str(play.length + 15), output_file, replay_file])
                    upscaled_filename = splitext(output_file)[0] + "_upscaled" + splitext(output_file)[1]
                    subprocess.run(
                        ["sh", "upscale.sh", str(COMPRESSION_CRF), output_file, upscaled_filename])
                    upload(upscaled_filename)
                except KeyError:
                    print("failed to record replay: object",
                          play_obj, "has no replay file")
                # except Exception as e:
                #     print("failed to record replay:", e)


def check_play_obj(play_obj):
    if play_obj.get("status") != "downloaded":
        print("replay was not downloaded successfully")
        return None
    if play := play_obj.get("play"):
        if not play.beatmap_name:
            print("play has no beatmap name")
            return None
        if not play.player_name:
            print("play has no player name")
            return None
        if not play.length:
            print("play has no length")
            return None
        else:
            if play.length > MAX_REPLAY_LENGTH:
                print("play is too long:", play.length)
                return None
        return play
    else:
        print("play_obj does not have a PlayDetails attached to it")


def upload(file_name):
    youtube = upload_youtube.get_authenticated_service(args=None)
    # too lazy to make a class so I'm using a mock
    Args = namedtuple('args', ["file", "keywords", "title", "description", "category", "privacyStatus"])
    args = Args(file_name, "keyword", "test title", "description", "22", "private")
    upload_youtube.initialize_upload(youtube, args)


if __name__ == "__main__":
    main()
