import praw
import io
import re



link_re = re.compile('\[.*?\]\(.*?\)')
url_re = re.compile('\(.*?\)')
# print(token)


def get_subreddit_links(reddit:praw.Reddit, subreddit:str, sort_type:str, num_posts:int, author:str):
    """
    Uses the Reddit instance to retrieve the first num_posts from subreddit, sorted by sort_type.
    Then searches for comments on these posts made by author (should be a bot that posts on all posts),
    and finally returns a dict where the keys are the post titles, and the values are a list of markdown-formatted
    links on that post by the given author. Only the first comment by author on each post is considered. 
    
    Only the first set of comments is loaded, so the comment by author should be pinned or highly upvoted.
    See praw api docs for list of valid sort types - https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html 
    """
    subreddit = reddit.subreddit(subreddit)
    link_set={}
    if sort_type == 'hot':
        submissions = subreddit.hot(limit=num_posts)
    elif sort_type == 'top':
        submissions = subreddit.top('day',limit=num_posts)
    for submission in submissions:
        # print("Title: " + submission.title)
        comments = submission.comments.list()
        link_list={} #heh
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


def parse_osu_links(d:dict):
    """
    Parse a dict of markdown-links sent by osu-bot. Extract the osu.ppy.sh URLs, and 
    """
    # out_str = "title;beatmap;download;mapper;player;top_on_map;top_play_of_top_on_map\n"
    new_d = {}
    for key,value in d.items():
        if value != []:
            # out_str = "{0}\n\"{1}\";".format(out_str,key)
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
    """
    Read token file and return a Reddit instance
    """
    try:
        token_file = io.open("creds/reddit_token.txt", "r")
        token = token_file.readlines()
        token_file.close()
        token[0] = token[0].rstrip('\n')
    except:
        print("unable to read Reddit API token")
        return None
    try:
        reddit = praw.Reddit(client_id=token[0],
                        client_secret=token[1],
                        user_agent='my user agent')
        # print(reddit.user.me())
        return reddit
    except:
        print("unable to initialize Reddit instance")

if __name__ == "__main__":
    links = get_subreddit_links(initialize(), 'osugame', 'top', 5, 'osu-bot')
    # print(links)
    # print('\n\n\n')
    print(parse_osu_links(links))