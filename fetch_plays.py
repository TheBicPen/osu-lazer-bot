import praw
import io
import re



link_re = re.compile('\[.*?\]\(.*?\)')
url_re = re.compile('\(.*?\)')
# print(token)


def get_subreddit_links(reddit:praw.Reddit, subreddit:str, sort_type:str, num_posts:int, author:str):
    subreddit = reddit.subreddit(subreddit)
    link_set={}
    if sort_type == 'hot':
        submissions = subreddit.hot(limit=num_posts)
    elif sort_type == 'top':
        submissions = subreddit.top('day',limit=num_posts)
    for submission in submissions:
        # print("Title: " + submission.title)
        comments = submission.comments.list()
        link_list=[] #heh
        try:
            for comment in comments:
                if comment.author == author:
                    # print(comment.body)
                    links = link_re.findall(comment.body)
                    for link in links:
                        link_list.append(link)
                    break
            link_set[submission.title] = link_list
        except Exception as e:
            print("Error while parsing comments" + e)
    return link_set


def parse_osu_links(d):
    out_str = "title;beatmap;download;mapper;player;top_on_map;top_play_of_top_on_map\n"
    new_d = {}
    for key,value in d.items():
        if value != []:
            out_str = "{0}\n\"{1}\";".format(out_str,key)
            new_val = []
            # beatmap, download, mapper, player, top_on_map, top_play_of_top_on_map = ""
            for link in value:
                # if "osu.ppy.sh/b/" in link and beatmap == "":
                #     beatmap = url_re.search(link).group(0)
                # elif "osu.ppy.sh/d/" in link and download == "":
                #     download = url_re.search(link).group(0)
                # elif "osu.ppy.sh/u/" in link and mapper == "":
                #     mapper = url_re.search(link).group(0)
                # elif "osu.ppy.sh/u/" in link and player == "":
                #     player = url_re.search(link).group(0)
                # elif "osu.ppy.sh/u/" in link and top_on_map == "":
                #     top_on_map = url_re.search(link).group(0)
                # elif "osu.ppy.sh/b/" in link and top_play_of_top_on_map == "":
                #     top_play_of_top_on_map = url_re.search(link).group(0)
                match = re.search("(http|https)://osu\.ppy\.sh/./\d*", link)
                if match is not None:
                    # out_str = "{0}{1};".format(out_str,re.sub("osu.ppy.sh/", "", match.group(0)))
                    # new_val.append(re.sub("osu.ppy.sh/./", "", match.group(0)))
                    new_val.append(match.group(0))
            new_d[key] = new_val
            # out_str = out_str + "\n"
        # out_str.append("{0},{1},{2},{3},{4},{5}\n".format(beatmap, download, mapper, player, top_on_map, top_play_of_top_on_map))
    return new_d
    # return out_str # am rarted

    # out ={}
    # for key,value in d.items():
    #     if value != []:
    #         out_value=[]
    #         for link in value:
    #             link = link[link.rfind('(')+1:-1]
    #             out_value.append(link)
    #     out[key] = value
    # return out

def initialize():
    token_file = io.open("creds/reddit_token.txt", "r")
    token = token_file.readlines()
    token_file.close()
    token[0] = token[0].rstrip('\n')
    if len(token) > 0:
        reddit = praw.Reddit(client_id=token[0],
                        client_secret=token[1],
                        user_agent='my user agent')
        # print(reddit.user.me())
        return reddit
    else:
        print("unable to get token")

if __name__ == "__main__":
    links = get_subreddit_links(initialize(), 'osugame', 'top', 5, 'osu-bot')
    # print(links)
    # print('\n\n\n\n\n\n\n\n\n')
    print(parse_osu_links(links))