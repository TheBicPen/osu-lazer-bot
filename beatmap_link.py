import fetch_plays as fp
import requests
import subprocess
import sys
import io


def auth_official():
    """
    Log in with credentials stored in creds/osu_credentials.txt and return session.
    Leave links as-is.
    """
    s = requests.session()
    try:
        with open('creds/osu_credentials.txt', 'r') as osu_creds:
            # username/password may end in a space, so we only strip the newline
            payload = {"username": osu_creds.readline().rstrip('\n'),
                       "password": osu_creds.readline().rstrip('\n'), "login": "Login"}
    except FileNotFoundError:
        print("Add your osu! username and password to the file 'creds/osu_credentials.txt'")
        try:
            with open('creds/osu_credentials.txt', 'w+') as osu_creds:
                osu_creds.writelines(["USERNAME\n", "PASSWORD\n"])
        except:
            print("Unable to create file")
        return

    # 302 on successful login, 200 on failure
    r = s.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload,
               headers={"Referer": "https://osu.ppy.sh/forum/ucp.php?mode=login"}, allow_redirects=False)

    if r.status_code == 302:
        return s
    elif r.status_code == 200:
        print("Failed to authenticate on official server. See 'downloads/post_login.html'")
        with open('downloads/post_login.html', 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    else:
        print("An error occurred while authenticating. Reason:", r.reason)


def auth_bloodcat(plays: list):
    """
    Return a session suitable for bloodcat (no auth required).
    Convert a link that to https://bloodacat.com/osu/s/<the original link's basename>
    """
    for i, play in enumerate(plays):
        plays[i].beatmapset_download = play.beatmapset_download.replace("https://osu.ppy.sh/d/",
                                                                        "https://bloodcat.com/osu/s/")
    return requests.Session()


def download(plays: list, filetype: str, auth_provider=None):
    """    
    Authenticate and convert links with auth_link and download objects (typically beatmaps) at links.
    Each file is saved to 'downloads/' with its name and being the text after the last '/'
    and the extension filetype.
    Return relative filenames of downloaded files.
    """

    if auth_provider == "official":
        s = auth_official()
    elif auth_provider == "bloodcat":
        s = auth_bloodcat(plays)
    else:
        s = auth_official()
        if not s:
            print("Using bloodcat mirror")
            s = auth_bloodcat(plays)

    # print(links)
    filenames = []
    for play in plays:
        link = play.beatmapset_download
        r = s.get(link)
        # print(link, r.reason)
        if r.ok:
            try:
                filename = f'downloads/beatmapset-{play.get_digits("beatmapset_download")}.{filetype}'
                with open(filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                # print(f"Downloaded beatmapset-{link}.osz")
                filenames.append(filename)
            except Exception as e:
                print("Failed to write response content to file", filename, e)
        else:
            print(f"Request for beatmapset-{play} failed because {r.reason}")
    return filenames


def main(download_option, download_script, max_plays_checked, reddit_sort_type, beatmap_provider=None):
    """
    Fetch r/osugame plays with options max_plays_checked and reddit_sort_type.
    Download beatmaps and/or replays based on the string in download_option using the script download_replays.
    Beatmaps are downloaded from beatmap_provider
    """

    plays = fp.get_osugame_plays(reddit_sort_type, max_plays_checked)
    out = {}
    print()
    if "beatmaps" in download_option:
        print("Downloading beatmaps")
        down_result = download(plays, "osz", auth_provider=beatmap_provider)
        out["beatmaps"] = down_result
        # print("Download result:\n", down_result)
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

        replay_infos = []
        for play in plays:
            try:
                replay_info = {"play": play}
                replay_infos.append(replay_info)
                helper_script = download_script.split()
                safe_player_name = fp.get_safe_name(play.player_name)
                output_file = f'downloads/mapset-{fp.get_digits(play.beatmapset_download)}_user-id-{safe_player_name}.osr'
                helper_script.extend(['--api-key', token, '--beatmap-id', fp.get_digits(play.beatmap_link), '--user-id',
                                      fp.get_digits(play.player_link), '--output-file', output_file])
                # print(f'Launching script {helper_script} to download replays')
                replay_info["replay_file"] = output_file
                try:
                    subprocess.run(helper_script).check_returncode()
                    replay_info["status"] = "downloaded"
                except subprocess.CalledProcessError as e:
                    print("Replay download script returned error", e)
                    replay_info["status"] = "error - download"
            except Exception as e:
                print("An error occurred while processing post",
                      play.post_title, e)
                replay_info["status"] = "error - pre-download"
        out["plays"] = replay_infos
    else:
        print("Skipping replay download")
    return out


if __name__ == "__main__":
    print(sys.argv)
    main(*sys.argv[1:])  # hope that all the args are provided
