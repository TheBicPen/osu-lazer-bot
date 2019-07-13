import fetch_plays as fp
import requests


def download(links):
    s = requests.session()
    payload = {"username": "", "password": "", "redirect": "index.php", "sid": "", "login":"Login"}
    r=s.get("https://osu.ppy.sh/forum/ucp.php?mode=login")
    r=s.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data=payload)
    r=s.get("https://osu.ppy.sh/forum/index.php?success=1563054777")
    print(r.content)
    for cookie in s.cookies:
        print(cookie)
    for link in links:
        r = s.get(link)
        print(r)
        # with open('out', 'wb') as fd:
        #     for chunk in r.iter_content(chunk_size=128):
        #         fd.write(chunk)

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