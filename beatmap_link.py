import fetch_plays as fp
import requests
import pickle


def download(links):
    s = requests.session()
    with open('creds/payload', 'rb') as handle:
        payload = pickle.loads(handle.read())
    r=s.get("https://osu.ppy.sh/forum/ucp.php?mode=login")
    with open('responses/get_login.html', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    r=s.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload)
    with open('responses/post_login.html', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    r=s.get("https://osu.ppy.sh/forum/index.php?success=1563054777")
    with open('responses/get_loggedin.html', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    for link in links:
        r = s.get(link)
        # print(r)
        with open('responses/last_link', 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

def get_links():
    links = fp.get_subreddit_links(fp.initialize(), 'osugame', 'top', 5, 'osu-bot')
    return fp.parse_osu_links(links)
    

def print_links(links):
    out=""
    for post,urls in links.items():
        # out = out+"https://osu.ppy.sh/d/"+urls[1] + "\n"
        print(post + " " + str(urls))
    return out

def get_download_links(links):
    out = []
    for post,urls in links.items():
        if len(urls) > 1:
            out.append(urls[1])
    return out

def main():
    links = get_links()
    print_links(links)
    download(get_download_links(links))

if __name__ == "__main__":
    main()