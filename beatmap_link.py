import fetch_plays as fp
import requests
import pickle
import subprocess
import sys
import io


def auth_official():
    """
    Log in with credentials stored in creds/payload (pickled) and return session.
    Leave links as-is.
    """
    s = requests.session()
    try:
        with open('creds/payload', 'rb') as handle:
            payload = pickle.loads(handle.read())
        r = s.get("https://osu.ppy.sh/forum/ucp.php?mode=login")
    except Exception as e:
        return "Failed to obtain osu credentials: {0}".format(e)
    r = s.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload)
    if not r.ok:
        with open('responses/post_login.html', 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        return "failed to authenticate:" + r.reason

    # no link processing

    return s


def get_digits(prepend: str, links: list):
    """
    Remove everything up to and including the last forward slash of each item in links
    and add the prefix prepend to it.
    """
    try:
        for i in range(len(links)):
            links[i] = prepend + links[i][links[i].rindex('/')+1:]
    except Exception as e:
        print(e)


def auth_bloodcat(links: list):
    """
    Return a session suitable for bloodcat (no auth required).
    Convert a link that to https://bloodacat.com/osu/s/<the original link's basename>
    """
    get_digits("https://bloodcat.com/osu/s/", links)
    return requests.Session()


def download(auth_link, links: list, filetype: str):
    """    
    Authenticate and convert links with auth_link and download objects (typically beatmaps) at links.
    Each file is saved to 'responses/downloads/' with its name and being the text after the last '/'
    and the extension filetype.
    Return relative filenames of downloaded files.
    """
    s = auth_link(links)
    print("Downloading links: ")
    print(links)
    stripped_links = []
    for link in links:
        r = s.get(link)
        print(link, r.reason)
        if r.ok:
            try:
                link_nums = link[link.rindex('/')+1:]
                filename = 'responses/downloads/{0}.{1}'.format(
                    link_nums, filetype)
                with open(filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                print("Downloaded {0}.osz".format(link))
                stripped_links.append(filename)
            except Exception as e:
                print("Failed to write response content to file " + filename, e)
        else:
            print("Request for {0} failed with reason {1}.".format(
                link, r.reason))
    return stripped_links


def download_replays(command: str, links: list):
    """
    Download replays by substituting the proper command arguments into command.
    Links is a list of lists. Each list descibes a play and contains 
    """


def print_links(links: dict):
    """
    Print a dictionary, parsing its values as strings. 
    Return a string of every value in links appended.
    """
    if len(links) == 0:
        print("no links in posts")
    out = ""
    print("Links in dict: ")
    for post, urls in links.items():
        print(post + " " + str(urls))
    return out


def get_beatmap_links(links: dict):
    """
    Takes a dict of lists, and returns a list of links to the beatmaps.
    """
    out = []
    for post, urls in links.items():
        if len(urls) > 1:
            out.append(urls[1])
    return out


def main(download_option, download_replays, max_plays_checked, max_plays_returned, reddit_sort_type):
    post_to_links = fp.get_subreddit_links(
        fp.initialize(), 'osugame', reddit_sort_type, int(max_plays_checked), 'osu-bot')  # get all osu-bot links
    # remove all links not pointing to osu.ppy.sh
    post_to_links = fp.parse_osu_links(post_to_links)
    # only get the top max_plays_returned most upvoted plays of the day
    while len(post_to_links) > int(max_plays_returned):
        post_to_links.popitem()

    if "beatmaps" in download_option:
        down_result = download(
            auth_bloodcat, get_beatmap_links(post_to_links), "osz")
        print("Download result: ")
        print(down_result)
    else:
        print("Skipping beatmap download")

    for title in post_to_links.keys():
        get_digits("", post_to_links[title])
    print_links(post_to_links)

    if "replays" in download_option:
        try:
            token_file = io.open("creds/osu_token.txt", "r")
            token = token_file.readline()
            token_file.close()
            token = token.rstrip('\n')
        except:
            print("unable to read osu! API token")
            return 
            
        download_replays = download_replays.split(' ')
        for post, links in post_to_links.items():
            try:
                helper_script = download_replays
                helper_script.extend(['--api-key', token, '--beatmap-id', links[0], '--user-id', links[4],
                            '--output-file', 'responses/downloads/{0}-{1}.osr'.format(links[0], links[4])])
                print('launching script {0} to download replays'.format(helper_script))
                retcode = subprocess.call(helper_script)
                if retcode != 0:
                    print("Helper script returned error code " + retcode)
            except:
                print("An error occurred while processing " + post)
    else:
        print("Skipping replay download")


if __name__ == "__main__":
    print(sys.argv)
    main(*sys.argv[1:])
