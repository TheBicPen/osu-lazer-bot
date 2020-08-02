
import beatmap_link
import subprocess
from fetch_plays import get_safe_name
from time import time

NUM_PLAYS_CHECKED = 8
SORT_TYPE = "hot"
DOWNLOAD_OPTION = "beatmaps replays"
REPLAY_DOWNLOAD_SCRIPT = "node osu-replay-downloader/fetch.js"
BEATMAP_LOAD_TIMEOUT = 10
REPLAY_LOAD_SLEEP = 5


def main():
    osu_command = ""
    with open("creds/osu_path.txt", "r") as f:
        osu_command = f.read().strip()
    with open("creds/recording_folder.txt", "r") as f:
        recording_folder = f.read().strip()
    downloads = beatmap_link.main(
        DOWNLOAD_OPTION, REPLAY_DOWNLOAD_SCRIPT, NUM_PLAYS_CHECKED, SORT_TYPE)
    if maps := downloads.get("beatmaps"):
        try:
            print("launching osu with beatmaps")
            subprocess.run([osu_command, *maps], timeout=BEATMAP_LOAD_TIMEOUT)
        except TimeoutError:
            print("osu! instance killed after loading maps")
    if plays := downloads.get("plays"):
        for play_obj in plays:
            if play_obj.get("status") == "downloaded":
                if play := play_obj.get("play"):
                    try:
                        output_file = recording_folder + \
                            get_safe_name(
                                f"/{play.beatmap_name}_{play.player_name}_{int(time())}.mkv")
                        replay_file = play_obj["replay_file"]
                        print("launching recording script with", replay_file)
                        subprocess.run(
                            ["sh", "launch.sh", REPLAY_LOAD_SLEEP, output_file, replay_file])
                        subprocess.run(["sh", "upscale.sh", 0, output_file])
                    except KeyError:
                        print("failed to record replay: object", play_obj, "has no replay file")
                    except:
                        print("failed to record replay")
                else:
                    print("play object does not have a valid play attached to it")
            else:
                print("replay was not downloaded successfully")


if __name__ == "__main__":
    main()
