import fetch_plays as fp
import requests
import subprocess
import sys
import io
from typing import List
import json


class BeatmapDownloader:
    """
    Base class for Beatmap downloaders.
    """
    _session: requests.Session = None

    def __init__(self):
        self._session = requests.Session()

    def download_beatmapset(self, digits, filename):
        pass

    def _write_response(self, response, filename):
        if response.ok:
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)
            return filename
        else:
            print(f"Request to download {filename} failed: {response.reason}")


class BloodcatProvider(BeatmapDownloader):
    """
    Download beatmaps from bloodcat mirror
    """

    def __init__(self):
        super().__init__()

    def download_beatmapset(self, digits, filename):
        r = self._session.get("https://bloodcat.com/osu/s/" + digits)
        return self._write_response(r, filename)


class OfficialProvider(BeatmapDownloader):
    """
    Download beatmaps from official site with credentials stored in creds/osu_credentials.txt
    """

    def __init__(self):
        super().__init__()
        try:
            with open('creds/osu_credentials.txt', 'r') as osu_creds:
                # username/password may end in a space, so we only strip the newline
                payload = {"username": osu_creds.readline().rstrip('\n'),
                           "password": osu_creds.readline().rstrip('\n'), "login": "Login"}
        except FileNotFoundError:
            print("Add your osu! username and password to 'creds/osu_credentials.txt'")
            try:
                with open('creds/osu_credentials.txt', 'w+') as osu_creds:
                    osu_creds.writelines(["USERNAME\n", "PASSWORD\n"])
            except:
                print("Unable to create file")
            raise FileNotFoundError
        # 302 on successful login, 200 on failure
        r = self._session.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload,
                               headers={"Referer": "https://osu.ppy.sh/forum/ucp.php?mode=login"}, allow_redirects=False)

        if r.status_code == 200:
            print("Failed to authenticate. See 'downloads/post_login.html'")
            with open('downloads/post_login.html', 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
            raise requests.HTTPError
        elif r.status_code != 302:
            print("An error occurred while authenticating. Reason:", r.reason)
            raise requests.HTTPError

    def download_beatmapset(self, digits, filename):
        r = self._session.get("https://osu.ppy.sh/d/" + digits)
        return self._write_response(r, filename)


class ReplayRecording:
    _beatmap_downloader: BeatmapDownloader = None
    play: fp.PlayDetails = None
    replay_file: str = None
    beatmap_file: str = None
    video_file: str = None
    video_title: str = None
    video_description: str = None
    video_tags: str = None
    video_category: str = None
    # video_visibility: str = None # only relevant at the upload step

    def __init__(self, play: fp.PlayDetails = None, beatmap_downloader: BeatmapDownloader = None, comment: str = None, title: str = None):

        if play is not None:
            self.play = play
        elif comment is not None and title is not None:
            self.play = fp.PlayDetails(comment, title)
        self._beatmap_downloader = beatmap_downloader

    def generate_video_attributes(self):
        # self._video_title = f"{self._play.player_name} | {self._play.beatmap_name}"
        self.video_title = self.play.post_title[:200]

        self.video_description = f"""{self.play.post_title}

        osu!lazer may show some extra misses/50s/100s. It is not perfectly accurate for stable replays.
        
        Player: {self.play.player_name} ({self.play.player_link})
        Mapper: {self.play.mapper_name} ({self.play.mapper_link})
        

        Check out this project on GitHub: https://github.com/TheBicPen/osu-lazer-bot
        
        """

        self.video_tags = ["osu", "osu!", "pp", "lazer", self.play.player_name,
                            self.play.beatmap_name, self.play.mapper_name, self.play.top_on_map].join(",")[:500]
        # gaming category as of 2020. I'm not spending API quota on this
        self.video_category = "22"

    def download_beatmapset(self, filename: str, provider=None):
        if provider is None:
            provider = self._beatmap_downloader
        self.beatmap_file = provider.download_beatmapset(
            fp.get_digits(self.play.beatmapset_download), filename)


def download_plays(download_option: str, max_plays_checked: int, reddit_sort_type: str, download_script: str = "node osu-replay-downloader/fetch.js", beatmap_provider=None) -> List[ReplayRecording]:
    """
    Check max_plays_checked r/osugame posts sorted by reddit_sort_type for plays.
    Download beatmaps and/or replays based on the string in download_option using the script download_replays.
    Beatmaps are downloaded using beatmap_provider
    """

    plays = fp.get_osugame_plays(reddit_sort_type, max_plays_checked)
    replay_infos = [ReplayRecording(play) for play in plays]
    print()
    if "beatmaps" in download_option:
        print("Downloading beatmaps")
        if beatmap_provider == "official":
            downloader = OfficialProvider()
        elif beatmap_provider == "bloodcat":
            downloader = BloodcatProvider()
        else:
            print("Trying to use official beatmap host")
            downloader = OfficialProvider()
            if not downloader:
                print("Falling back to bloodcat beatmap host")
                downloader = BloodcatProvider()
        for replay_info in replay_infos:
            try:
                safe_beatmap_name = fp.get_safe_name(
                    replay_info.play.beatmap_name)
                replay_info.download_beatmapset(
                    f"downloads/{safe_beatmap_name}.osz", downloader)
            except:
                print("Failed to download beatmap")
                if replay_info.play is not None:
                    print(
                        f"Beatmap name: {replay_info.play.beatmap_name}, post title: '{replay_info.play.post_title}'")
    else:
        print("Skipping beatmap download")

    print()
    if "replays" in download_option:
        print("Downloading replays")
        try:
            with open("creds/osu_token.txt", "r") as token_file:
                token = token_file.readline().rstrip()
        except IOError as e:
            print("Unable to read osu! API token:", e)
            return

        for replay_info in replay_infos:
            try:
                helper_script = download_script.split()
                play = replay_info.play
                safe_player_name = fp.get_safe_name(play.player_name)
                safe_beatmap_name = fp.get_safe_name(
                    replay_info.play.beatmap_name)
                output_file = f'downloads/{safe_beatmap_name}_{safe_player_name}.osr'
                helper_script.extend([
                    '--api-key', token,
                    '--beatmap-id', str(fp.get_digits(play.beatmap_link)),
                    '--user-id', str(fp.get_digits(play.player_link)),
                    '--mods', str(play.mods_bitmask),
                    '--output-file', output_file
                ])
                subprocess.run(helper_script).check_returncode()
                replay_info.replay_file = output_file
            except subprocess.CalledProcessError as e:
                if play is None:
                    print("There is no play object attached (!?)")
                else:
                    print(f"Failed to download replay of {play.player_name} - {play.beatmap_name}\n",
                          # e
                          )
            except AttributeError as e:
                if play is None:
                    print("There is no play object attached to replay info",
                          replay_info.__dict__)
                else:
                    print(f"Play '{play.post_title}' is missing required information:",
                          f"\nPlayer name:{play.player_name}, link:{play.player_link}",
                          f"\nBeatmap name:{play.beatmap_name}, link:{play.beatmap_link}, mapset link:{play.beatmapset_download}",
                          f"\nMods:{play.mods_string}, bitmask:{play.mods_bitmask}",
                          f"\nLength:{play.length}",
                          "\n")
            # except Exception as e:
            #     print("An error occurred while processing post",
            #           replay_info.play.post_title, e)
    else:
        print("Skipping replay download")
    return replay_infos


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(sys.argv)
        replay_recordings = download_plays(*sys.argv[1:])
    else:
        replay_recordings = download_plays("beatmaps replays", 8, "hot")
    # print(json.dumps(replay_recordings))
    # with open("plays.json", "w+") as outfile:
    #     json.dump(replay_recordings, outfile)
