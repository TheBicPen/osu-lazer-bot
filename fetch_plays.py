import praw
import io
import re


osu_link = "(http|https)://osu\.ppy\.sh/./\d*"
link_re = re.compile('\[.*?\]\(.*?\)')
url_re = re.compile('\(.*?\)')


def get_subreddit_links(reddit: praw.Reddit, subreddit: str, sort_type: str, num_posts: int, author: str):
    """
    Uses the Reddit instance to retrieve the first num_posts from subreddit, sorted by sort_type.
    Then searches for comments on these posts made by author (should be a bot that posts on all posts),
    and finally returns a list of lists of markdown-formatted links on that post by the given author.
    Only the first comment by author on each post is considered. 

    Only the first set of comments is loaded, so the comment by author should be pinned or highly upvoted.
    See praw api docs for list of valid sort types - https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html 
    """
    subreddit = reddit.subreddit(subreddit)
    link_set = {}
    num_posts=int(num_posts)
    if sort_type == 'hot':
        submissions = subreddit.hot(limit=num_posts)
    elif sort_type in ['hour', 'day', 'week', 'month', 'year', 'all']:
        submissions = subreddit.top(sort_type, limit=num_posts)
    for submission in submissions:
        comments = submission.comments.list()
        try:
            for comment in comments:
                if comment.author == author:
                    link_set[submission.title] = link_re.findall(comment.body)
                    break
            if submission.title not in link_set.keys():
                print("Post titled %s has no comments by %s in the first 50 comments".format(submission.title, author))
        except Exception as e:
            print("Error while parsing comments", e)
    return link_set


def parse_osu_links(d: dict):
    """
    Parse a dict of markdown-links sent by osu-bot. Extract the osu.ppy.sh URLs,
    and return a dict where keys are unchanged, but the values are the URLs.

    link format: beatmap, download, mapper, top_on_map, player, top_play_of_player
    """
    new_d = {}
    for key, value in d.items():
        if value != []:
            new_val = []
            for link in value:
                match = re.search(osu_link, link)
                if match is not None:
                    new_val.append(match.group(0))
            new_d[key] = new_val
    return new_d


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
        return reddit
    except:
        print("unable to initialize Reddit instance")


if __name__ == "__main__":
    plays_to_linkset = get_subreddit_links(
        initialize(), 'osugame', 'top', 5, 'osu-bot')
    print(parse_osu_links(plays_to_linkset))
