import fetch_plays as fp

links = fp.get_subreddit_links(fp.initialize(), 'osugame', 'top', 5, 'osu-bot')
links = fp.parse_osu_links(links)

out=""
for post,urls in links.items():
    out = out+"https://osu.ppy.sh/d/"+urls[1] + "\n"
print(out)