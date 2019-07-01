import praw
import io
import re

token_file = io.open("creds/reddit_token.txt", "r")
token = token_file.readlines()
token_file.close()
token[0] = token[0].rstrip('\n')

link_re = re.compile('\[.*?\]\(.*?\)')
print(token)

if len(token) > 0:
    reddit = praw.Reddit(client_id=token[0],
                     client_secret=token[1],
                     user_agent='my user agent')
    # print(reddit.user.me())

    osugame = reddit.subreddit('osugame')
    for submission in osugame.top('day',limit=5):
        print("Title:" + submission.title)
        comments = submission.comments.list()
        for comment in comments:
            if comment.author == 'osu-bot':
                # print(comment.body)
                print(link_re.findall(comment.body))