import praw
import re


class PlayDetails:
    beatmap_name = None
    beatmap_link=None
    beatmapset_download = None
    mapper_name = None
    mapper_link = None
    top_on_map = None
    player_name = None
    player_link = None
    top_play_of_player = None
    post_title = None
    comment_text = None

    _beatmap_re = re.compile(r"#### \[(.+?\[.+?\])\]\((https?://osu\.ppy\.sh/b/\d+[^\)\s]+)\)")
    _beatmapset_download_re = re.compile(r"\[\(&#x2b07;\)\]\((https?://osu\.ppy\.sh/d/\d+)\s*\"Download this beatmap\"\)")
    _mapper_re = re.compile(r"by \[(.*)\]\((https?://osu\.ppy\.sh/u/\d+)\s*\"\d+ ranked, \d+ qualified, \d+ loved, \d+ unranked\"\)")
    _player_re = re.compile(r"Top Play[\s\S\n]*?\[(.+?)\]\((https?://osu\.ppy\.sh/u/\d+)(?:\s*?\"Previously known as \'.+?\'\")?\)")

    def __init__(self, comment, title):
        self.post_title = title
        self.comment_text = comment
        if match := re.search(self._beatmapset_download_re, comment):
            self.beatmapset_download = match.group(1)
        if match := re.match(self._beatmap_re, comment):
            self.beatmap_name, self.beatmap_link = match.group(1,2)
        if match := re.search(self._mapper_re, comment):
            self.mapper_name, self.mapper_link = match.group(1,2)
        if match := re.search(self._player_re, comment):
            self.player_name, self.player_link = match.group(1,2)
    
    def get_digits(self, prop_name: str):
        """
        Return only the digits of a PlayDetails property by name.
        """
        prop_val=None
        if prop_name == "beatmap_link":
            prop_val = self.beatmap_link
        elif prop_name == "beatmapset_download":
            prop_val = self.beatmapset_download
        elif prop_name == "mapper_link":
            prop_val = self.mapper_link
        elif prop_name == "player_link":
            prop_val = self.player_link
        if prop_val:
            last_slash = prop_val.rfind('/')
            return prop_val[last_slash + 1:] if last_slash != -1 else ""
        return None


def get_osugame_plays(sort_type: str, num_posts: int):
    """
    This is where I realized just how obtuse the rest of the code in this file is
    This function handles the whole process.
    """
    reddit = initialize()
    score_posts = get_subreddit_links(reddit, "osugame", sort_type, num_posts, "osu-bot")
    plays=[]
    for title, comment_body in score_posts.items():
        try:
            plays.append(PlayDetails(comment_body, title))
        except Exception as e:
            print(f"Error parsing post '{title}':\n{e}")
            pass
    return plays



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
    num_posts = int(num_posts)
    post_to_comment_by_author = {}
    if sort_type == 'hot':
        submissions = subreddit.hot(limit=num_posts)
    elif sort_type in ['hour', 'day', 'week', 'month', 'year', 'all']:
        submissions = subreddit.top(sort_type, limit=num_posts)
    else:
    #     submissions = subreddit.top('week', limit=num_posts)
        return
    for submission in submissions:
        submission.comments.replace_more(0) # we want top level comments only
        comments = submission.comments.list()
        try:
            for comment in comments:
                if isinstance(comment, praw.models.MoreComments):
                    print(f"No top comments by {author} in post '{submission.title}'")
                elif comment.author == author:
                    post_to_comment_by_author[submission.title] = comment.body
                    break
            if submission.title not in post_to_comment_by_author.keys():
                print(f"Not a score post: '{submission.title}'")
        except Exception as e:
            print("Error while parsing comments", e)
    return post_to_comment_by_author



def initialize():
    """
    Read token file and return a Reddit instance.
    1st line of file is client id, 2nd line is secret.
    """
    try:
        with open("creds/reddit_token.txt", "r") as token_file:
            token = token_file.readlines()
        token[0] = token[0].strip()
    except:
        print("unable to read Reddit API token")
        return
    try:
        reddit = praw.Reddit(client_id=token[0],
                             client_secret=token[1],
                             user_agent='my user agent')
        return reddit
    except:
        print("unable to initialize Reddit instance")

if __name__ == "__main__":
    print(get_osugame_plays("week", 10))
