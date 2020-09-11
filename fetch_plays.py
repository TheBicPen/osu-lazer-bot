import praw
import re

# osu-bot constants taken from https://github.com/christopher-dG/osu-bot/blob/master/osubot/consts.py
mods2int = {
    # "": 1 >> 1,
    "NF": 1 << 0,
    "EZ": 1 << 1,
    "TD": 1 << 2,
    "HD": 1 << 3,
    "HR": 1 << 4,
    "SD": 1 << 5,
    "DT": 1 << 6,
    "RX": 1 << 7,
    "HT": 1 << 8,
    "NC": 1 << 6 | 1 << 9,  # DT is always set along with NC.
    "FL": 1 << 10,
    "AT": 1 << 11,
    "SO": 1 << 12,
    "AP": 1 << 13,
    "PF": 1 << 5 | 1 << 14,  # SD is always set along with PF.
    "V2": 1 << 29,
    # TODO: Unranked Mania mods, maybe.
}

class PlayDetails:
    beatmap_name = None
    beatmap_link = None
    beatmapset_download = None
    mapper_name = None
    mapper_link = None
    top_on_map = None
    player_name = None
    player_link = None
    top_play_of_player = None
    post_title = None
    comment_text = None
    length = None
    mods_bitmask = None
    mods_string = None

    _beatmap_re = re.compile(
        r"#### \[(.+?\[.+?\])\]\((https?://osu\.ppy\.sh/b/\d+[^\)\s]+)\)")
    _beatmapset_download_re = re.compile(
        r"\[\(&#x2b07;\)\]\((https?://osu\.ppy\.sh/d/\d+)\s*\"Download this beatmap\"\)")
    _mapper_re = re.compile(
        r"by \[(.*)\]\((https?://osu\.ppy\.sh/u/\d+)( \"(\d+) ranked, (\d+) qualified, (\d+) loved, (\d+) unranked\")?\)")
    _player_re = re.compile(
        r"\[(.+?)\]\((https?://osu\.ppy\.sh/u/\d+)(?:\s*?\"Previously known as \'.+?\'\")?\)\s+\|\s+#\d+")
    _length_re = re.compile(
        r"\|(?:[^\|\n]+\|)+\s+(\d+:\d+)\s+\|(?:[^\|\n]+\|)+")
    _mods_re = re.compile(r"\|\s+\+(\w+)\s+\|(?:[^\|\n]+\|)+")

    def __init__(self, comment: str, title: str):
        self.post_title = title
        self.comment_text = comment
        if match := re.search(self._beatmapset_download_re, comment):
            self.beatmapset_download = match.group(1)
        if match := re.search(self._beatmap_re, comment):
            self.beatmap_name, self.beatmap_link = match.group(1, 2)
        if match := re.search(self._mapper_re, comment):
            self.mapper_name, self.mapper_link = match.group(1, 2)
        if match := re.search(self._player_re, comment):
            self.player_name, self.player_link = match.group(1, 2)
        if matches := re.findall(self._length_re, comment):
            try:
                time_str = matches[-1].split(":")
                self.length = 60 * int(time_str[0]) + int(time_str[1])
            except:
                print("Failed to parse map length")
        if self.beatmap_name:
            self.mods_bitmask = 0
            if match := re.search(self._mods_re, comment):
                self.mods_string = match.group(1)
                for mod in mods2int:
                    if mod in self.mods_string:
                        self.mods_bitmask += mods2int[mod]


def get_safe_name(string):
    if string is None:
        return None
    return "".join([x if x.isalnum() else "_" for x in string])


def get_digits(link):
    last_slash = link.rfind('/')
    return link[last_slash + 1:] if last_slash != -1 else None


def get_osugame_plays(sort_type: str, num_posts: int):
    """
    This function handles the whole process.
    Here I realized just how obtuse the rest of the code in this file is
    """
    reddit = initialize()
    score_posts = get_subreddit_links(
        reddit, "osugame", sort_type, num_posts, "osu-bot")
    plays = []
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
        return
    for submission in submissions:
        submission.comments.replace_more(0)  # we want top level comments only
        comments = submission.comments.list()
        try:
            for comment in comments:
                if isinstance(comment, praw.models.MoreComments):
                    print(
                        f"No top comments by {author} in post '{submission.title}'")
                elif comment.author == author:
                    post_to_comment_by_author[submission.title] = comment.body
                    print(f"Score post: '{submission.title}'")
                    break
            if submission.title not in post_to_comment_by_author.keys():
                print(f"Not a score post: '{submission.title}'")
        except Exception as e:
            print("Error while parsing comments", submission.title)
            print(e)
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
