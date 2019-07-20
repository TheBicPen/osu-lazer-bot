import fetch_plays as fp
import requests
import pickle
import sys


def download(links:list, filetype:str):
    """
    Log in with credentials stored in creds/payload (pickled), 
    download objects (typically beatmaps) at links, and save each one with 
    the provided file extension.
    """
    s = requests.session()
    try:
        with open('creds/payload', 'rb') as handle:
            payload = pickle.loads(handle.read())
        r=s.get("https://osu.ppy.sh/forum/ucp.php?mode=login")
    except Exception as e:
        return "Failed to obtain osu credentials: {0}".format(e)
    # with open('responses/get_login.html', 'wb') as fd:
        # for chunk in r.iter_content(chunk_size=128):
        #     fd.write(chunk)
    r=s.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload)
    # with open('responses/post_login.html', 'wb') as fd:
        # for chunk in r.iter_content(chunk_size=128):
        #     fd.write(chunk)
    if not r.ok:
        return "failed to authenticate:" + r.reason
    # r=s.get("https://osu.ppy.sh/forum/index.php?success=1563054777")
    # with open('responses/get_loggedin.html', 'wb') as fd:
    #     for chunk in r.iter_content(chunk_size=128):
    #         fd.write(chunk)
    stripped_links = []
    for link in links:
        r = s.get(link)
        print(link, r.reason)
        if r.ok:
            try:
                link_nums = link[link.rindex('/')+1:]
                with open('responses/downloads/{0}.{1}'.format(link_nums, filetype), 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                print("Downloaded {0}.osz".format(link))
                stripped_links.append(link_nums)
            except Exception as e:
                print("Failed to write response content to file", e)
        else:
            print("Request for {0} failed with reason {1}.".format(link, r.reason))
    return stripped_links

def print_links(links:list):
    if len(links) == 0:
        print("no links in posts")
    out=""
    for post,urls in links.items():
        # out = out+"https://osu.ppy.sh/d/"+urls[1] + "\n"
        print(post + " " + str(urls))
    return out

def get_beatmap_links(links:dict):
    """
    Takes a dict of lists, and returns a list of links to the beatmaps.
    """
    out = []
    for post,urls in links.items():
        if len(urls) > 1:
            out.append(urls[1])
    return out

def main():
    post_to_links = fp.get_subreddit_links(fp.initialize(), 'osugame', 'top', 10, 'osu-bot')
    post_to_links = fp.parse_osu_links(post_to_links)
    while len(post_to_links) > 2:      # only get the top plays of the day
        post_to_links.popitem()
    print_links(post_to_links)
    # download(get_beatmap_links(post_to_links), "osz")
    raw_links = []
    try:
        for title,osu_links in post_to_links.items():
            for link in osu_links:
                raw_links.append(link[link.rindex('/')+1:])
    except Exception as e:
        print(e)
    print(raw_links)
    

if __name__ == "__main__":
    main()