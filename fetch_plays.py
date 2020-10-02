import praw
import re
from typing import List
import json

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

PLAYER_SKIP_LIST_FILE = "creds/skip_players.txt"
SCORE_SKIP_LIST_FILE = "creds/skip_plays.txt"


class ScorePostInfo:

    _beatmap_re = re.compile(
        r"#### \[(.+?\[.+?\])\]\((https?://osu\.ppy\.sh/b/\d+[^\)\s]+)\)")
    _beatmapset_download_re = re.compile(
        r"\[\(&#x2b07;\)\]\((https?://osu\.ppy\.sh/d/\d+)\s*\"Download this beatmap\"\)")
    _mapper_re = re.compile(
        r"by \[(.+?)\]\((https?://osu\.ppy\.sh/u/\d+)( \"[^\"]+\")?\)")
    _player_re = re.compile(
        r"\[(.+?)\]\((https?://osu\.ppy\.sh/u/\d+)(?:\s*?\"Previously known as \'.+?\'\")?\)\s+\|\s+#\d+")
    _length_re = re.compile(
        r"\|(?:[^\|\n]+\|)+\s+(\d+:\d+)\s+\|(?:[^\|\n]+\|)+")
    _mods_re = re.compile(r"\|\s+\+(\w+)\s+\|(?:[^\|\n]+\|)+")

    def __init__(self, comment: praw.Reddit.comment = None, comment_text: str = None, post_title: str = None):
        """ 
        Pass in either comment or comment_text and post_title.
        Comment object is preferred - the other 2 are kept only for unit testing. (I'm too lazy to make a mock)
        """
        self.beatmap_name = None
        self.beatmap_link = None
        self.beatmapset_download = None
        self.mapper_name = None
        self.mapper_link = None
        self.top_on_map = None
        self.player_name = None
        self.player_link = None
        self.top_play_of_player = None
        self.post_title = None
        self.post_id = None
        self.comment_text = None
        self.comment_id = None
        self.length = None
        self.mods_bitmask = None
        self.mods_string = None

        if comment is not None:
            self.post_title = comment.submission.title
            self.comment_text = comment.body
            self.comment_id = comment.id
            self.post_id = comment.submission.id
        elif post_title is not None and comment_text is not None:
            self.post_title = post_title
            self.comment_text = comment_text

        self.set_beatmap(self.comment_text)

        if match := re.search(self._mapper_re, self.comment_text):
            self.mapper_name, self.mapper_link = match.group(1, 2)
        if match := re.search(self._player_re, self.comment_text):
            self.player_name, self.player_link = match.group(1, 2)
        if matches := re.findall(self._length_re, self.comment_text):
            try:
                time_str = matches[-1].split(":")
                self.length = 60 * int(time_str[0]) + int(time_str[1])
            except Exception:
                print("Failed to parse map length")
        if self.beatmap_name:
            self.mods_bitmask = 0
            if match := re.search(self._mods_re, self.comment_text):
                self.set_mods(match.group(1))

    def __str__(self):
        return "Play: {\n\t%s\n}" % "\n\t".join([f"'{k}': {v}" for k, v in self.__dict__.items()])

    def set_mods(self, mods_string: str):
        self.mods_string = mods_string
        if self.mods_bitmask is None:
            self.mods_bitmask = 0
        for mod in mods2int:
            if mod in self.mods_string:
                self.mods_bitmask += mods2int[mod]

    def set_beatmap(self, comment: str):
        if match := re.search(self._beatmapset_download_re, comment):
            self.beatmapset_download = match.group(1)
        if match := re.search(self._beatmap_re, comment):
            self.beatmap_name, self.beatmap_link = match.group(1, 2)

    def set_beatmap_url(self, url: str):
        beatmap_url_re = re.compile(
            r"https?://osu\.ppy\.sh/beatmapsets/(\d+)#(\w+)/(\d+)")
        mode2int = {
            "osu": 0,
            "taiko": 1,
            "fruits": 2,
            "mania": 3
        }
        if match := re.match(beatmap_url_re, url):
            self.beatmapset_download = "https://osu.ppy.sh/d/" + match.group(1)
            self.beatmap_link = f"https://osu.ppy.sh/b/{match.group(3)}?m={mode2int.get(match.group(2), 0)}"
            return True
        return False


def get_safe_name(string):
    if string is None:
        return None
    return "".join([x if x.isalnum() else "_" for x in string])


def get_digits(link):
    last_slash = link.rfind('/')
    return link[last_slash + 1:] if last_slash != -1 else None


def get_osugame_plays(sort_type: str, num_posts: int, reddit: praw.reddit = None):
    """
    This function handles the whole process.
    Here I realized just how obtuse the rest of the code in this file is
    """
    if reddit is None:
        reddit = initialize()
    score_posts = get_score_posts(
        reddit, "osugame", sort_type, num_posts, "osu-bot")
    return score_posts


def post_vid_to_reddit(vid_id: str, post_id: str, reddit: praw.Reddit = None):
    if vid_id is None or post_id is None:
        return
    comment = "lazer replay https://www.youtube.com/watch?v=" + vid_id
    if reddit is None:
        reddit = initialize()
    return reddit.submission(id=post_id).reply(comment)


def get_scorepost_by_id(id: str, reddit: praw.Reddit = None):
    if reddit is None:
        reddit = initialize()
    post = reddit.submission(id=id)
    if comment := get_scorepost_comment(post, "osu-bot"):
        return ScorePostInfo(comment)
    return None


def filter_playernames(scores: List[ScorePostInfo], skip_list=PLAYER_SKIP_LIST_FILE):
    """
    Filter scoreposts whose player link is in the file skip_list.
    Does not mutate the original list.
    """
    with open(skip_list, "r+") as f:
        skip_list = [line.strip() for line in f.readlines()]
    return [score for score in scores if score.player_link not in skip_list]


def filter_scoreposts(scores: List[ScorePostInfo], skip_list=SCORE_SKIP_LIST_FILE):
    """
    Filter scoreposts that contain duplicates, where equality is determined by the dict returned by make_score_info.
    Does not mutate the original list
    """
    with open(skip_list, "r+") as f:
        skip_list = json.load(f)
    return [score for score in scores if make_score_info(score) not in skip_list]


def make_score_info(score: ScorePostInfo):
    """
    Return a dict of some key properties of a play that can be used to determine whether 2 posts are of the same play.
    This is designed to not consider posts with incomplete information to be the same as posts with complete info
    """
    return {'player_link': score.player_link, 'map': score.beatmap_link, 'mods': score.mods_string}


def add_score_info_to_skiplist(score: ScorePostInfo, skip_list=SCORE_SKIP_LIST_FILE):
    with open(skip_list, "r+") as f:
        skip_list = json.load(f)
        skip_list.append(make_score_info(score))
        f.seek(0)
        f.truncate()
        json.dump(skip_list, f)


def get_score_posts(reddit: praw.Reddit, subreddit: str, sort_type: str, num_posts: int, author: str, use_skiplist=False):
    """
    Uses the Reddit instance to retrieve the first num_posts from subreddit, sorted by sort_type.
    Then searches for top-level comments on these posts made by author (should be a bot that posts on all posts).
    Only the first set of comments is loaded, so the comment by author should be pinned or highly upvoted.
    Only the first comment by author on each post is considered.
    """
    subreddit = reddit.subreddit(subreddit)
    num_posts = int(num_posts)
    scoreposts = []
    if sort_type == 'hot':
        posts = subreddit.hot(limit=num_posts)
    elif sort_type in ['hour', 'day', 'week', 'month', 'year', 'all']:
        posts = subreddit.top(sort_type, limit=num_posts)
    else:
        return
    if use_skiplist:
        with open("creds/skip_posts.txt", "r+") as f:
            skip_list = [line.strip() for line in f.readlines()]
    for post in posts:
        if use_skiplist and post.id in skip_list:
            print(f"Skipping post '{post.title}'")
            continue
        if comment := get_scorepost_comment(post, author):
            print(f"Score post: '{post.title}'")
            scoreposts.append(ScorePostInfo(comment))
        else:
            print(f"Not a score post: '{post.title}'")
    return scoreposts


def get_scorepost_comment(post: praw.Reddit.submission, author: str):
    """
    Return top-level comment by author or None if none is found.
    """
    comments = post.comments.list()
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            # print(f"No top-level comments by {author} in post '{post.title}'")
            pass
        elif comment.author == author:
            return comment
    else:
        return None


def initialize():
    """
    Read token file and return a Reddit instance.
    1st line of file is client id, 2nd line is secret.
    """
    try:
        with open("creds/reddit_token.txt", "r") as token_file:
            token = token_file.readlines()
        token[0] = token[0].strip()
    except Exception:
        print("Unable to read Reddit API token")
        return
    try:
        reddit = praw.Reddit(client_id=token[0],
                             client_secret=token[1],
                             user_agent='lazerbot post parser - https://github.com/TheBicPen/osu-lazer-bot')
        return reddit
    except Exception:
        print("Unable to initialize Reddit instance")


if __name__ == "__main__":
    print(get_osugame_plays("week", 10))
