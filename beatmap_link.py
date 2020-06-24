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
        print("Failed to authenticate on official server. See 'responses/post_login.html'")
        with open('responses/post_login.html', 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    else:
        print("An error occurred while authenticating. Reason:", r.reason)


def auth_bloodcat(links: list):
    """
    Return a session suitable for bloodcat (no auth required).
    Convert a link that to https://bloodacat.com/osu/s/<the original link's basename>
    """
    for i, link in enumerate(links):
        links[i] = link.replace("https://osu.ppy.sh/d/",
                                "https://bloodcat.com/osu/s/")
    return requests.Session()


def download(links: list, filetype: str, auth_provider=None):
    """    
    Authenticate and convert links with auth_link and download objects (typically beatmaps) at links.
    Each file is saved to 'responses/downloads/' with its name and being the text after the last '/'
    and the extension filetype.
    Return relative filenames of downloaded files.
    """

    if auth_provider == "official":
        s = auth_official()
    elif auth_provider == "bloodcat":
        s = auth_bloodcat(links)
    else:
        s = auth_official()
        if not s:
            print("Using bloodcat mirror")
            s = auth_bloodcat(links)

    # print(links)
    stripped_links = []
    for link in links:
        r = s.get(link)
        # print(link, r.reason)
        if r.ok:
            try:
                link_nums = link[link.rindex('/')+1:]
                filename = f'responses/downloads/beatmapset-{link_nums}.{filetype}'
                with open(filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                # print(f"Downloaded beatmapset-{link}.osz")
                stripped_links.append(filename)
            except Exception as e:
                print("Failed to write response content to file", filename, e)
        else:
            print(f"Request for beatmapset-{link} failed because {r.reason}")
    return stripped_links


def main(download_option, download_script, max_plays_checked, reddit_sort_type, beatmap_provider=None):
    """
    Fetch r/osugame plays with options max_plays_checked and reddit_sort_type.
    Download beatmaps and/or replays based on the string in download_option using the script download_replays.
    Beatmaps are downloaded from beatmap_provider

    Verbosity levels: 0 - errors only, 1 - minimum info, 2 - maximum info
    """

    plays = fp.get_osugame_plays(reddit_sort_type, max_plays_checked)

    print()
    if "beatmaps" in download_option:
        print("Downloading beatmaps")
        beatmapset_links = [
            play.beatmapset_download for play in plays if play.beatmapset_download]
        down_result = download(beatmapset_links, "osz",
                               auth_provider=beatmap_provider)
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

        for play in plays:
            try:
                helper_script = download_script.split()
                safe_player_name = "".join(
                    [x if x.isalnum() else "_" for x in play.player_name])
                output_file = f'responses/downloads/mapset-{play.get_digits("beatmapset_download")}_user-id-{safe_player_name}.osr'
                helper_script.extend(['--api-key', token, '--beatmap-id', play.get_digits("beatmap_link"), '--user-id',
                                      play.get_digits("player_link"), '--output-file', output_file])
                # print(f'Launching script {helper_script} to download replays')
                try:
                    subprocess.run(helper_script).check_returncode()
                except subprocess.CalledProcessError as e:
                    print("Replay download script returned error", e)
            except Exception as e:
                print("An error occurred while processing post",
                      play.post_title, e)
    else:
        print("Skipping replay download")


if __name__ == "__main__":
    print(sys.argv)
    main(*sys.argv[1:])  # hope that all the args are provided
