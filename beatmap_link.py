import fetch_plays as fp
import requests
import pickle
import subprocess
import sys
import io

# ew global
verbosity = 1
"""
Verbosity levels: 0 - errors only, 1 - minimum info, 2 - maximum info
"""


def auth_official():
    """
    Log in with credentials stored in creds/payload (pickled) and return session.
    Leave links as-is.
    """
    s = requests.session()
    try:
        with open('creds/payload', 'rb') as handle:
            payload = pickle.load(handle)
        r = s.get("https://osu.ppy.sh/forum/ucp.php?mode=login")
    except Exception as e:
        print("Failed to obtain osu credentials:", e)
        return
    r = s.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload)
    if not r.ok:
        with open('responses/post_login.html', 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        print("Failed to authenticate:" + r.reason)
        return

    # no link processing

    return s


def auth_bloodcat(links: list):
    """
    Return a session suitable for bloodcat (no auth required).
    Convert a link that to https://bloodacat.com/osu/s/<the original link's basename>
    """
    for i, link in enumerate(links):
        try:
            links[i] = "https://bloodcat.com/osu/s/" + link[link.rindex('/')+1:]
        except Exception as e:
            print(e)
    return requests.Session()


def download(auth_provider, links: list, filetype: str):
    """    
    Authenticate and convert links with auth_link and download objects (typically beatmaps) at links.
    Each file is saved to 'responses/downloads/' with its name and being the text after the last '/'
    and the extension filetype.
    Return relative filenames of downloaded files.
    """

    # adapter for authentication (basically an inline function)
    s = None
    if auth_provider == "official":
        s = auth_official()
    elif auth_provider == "bloodcat":
        s = auth_bloodcat(links)
    else:
        print(f"Invalid beatmap provider {auth_provider}. Using default 'official'")
        s = auth_official()

    if verbosity > 1:
        print(links)
    stripped_links = []
    for link in links:
        r = s.get(link)
        if verbosity > 1:
            print(link, r.reason)
        if r.ok:
            try:
                link_nums = link[link.rindex('/')+1:]
                filename = f'responses/downloads/beatmapset-{link_nums}.{filetype}'
                with open(filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                if verbosity > 1:
                    print(f"Downloaded beatmapset-{link}.osz")
                stripped_links.append(filename)
            except Exception as e:
                print("Failed to write response content to file", filename, e)
        else:
            print(f"Request for beatmapset-{link} failed because {r.reason}")
    return stripped_links


def main(download_option, download_script, max_plays_checked, reddit_sort_type, beatmap_provider="official", verbosity_arg=1):
    """
    Fetch r/osugame plays with options max_plays_checked and reddit_sort_type.
    Download beatmaps and/or replays based on the string in download_option using the script download_replays

    Verbosity levels: 0 - errors only, 1 - minimum info, 2 - maximum info
    """
    verbosity = int(verbosity_arg)

    plays = fp.get_osugame_plays(reddit_sort_type, max_plays_checked)

    if "beatmaps" in download_option:
        if verbosity > 0:
            print("Downloading beatmaps")
        beatmapset_links = [
            play.beatmapset_download for play in plays if play.beatmapset_download]
        down_result = download(beatmap_provider, beatmapset_links, "osz")
        if verbosity > 1:
            print("Download result:\n", down_result)
    else:
        if verbosity > 0:
            print("Skipping beatmap download")

    if "replays" in download_option:
        if verbosity > 0:
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
                if verbosity > 1:
                    print(
                        f'Launching script {helper_script} to download replays')
                try:
                    subprocess.run(helper_script).check_returncode()
                except subprocess.CalledProcessError as e:
                    print("replay download script returned error", e)
            except Exception as e:
                print("An error occurred while processing post",
                      play.post_title, e)
    else:
        if verbosity > 0:
            print("Skipping replay download")


if __name__ == "__main__":
    print(sys.argv)
    main(*sys.argv[1:])  # hope that all the args are provided
