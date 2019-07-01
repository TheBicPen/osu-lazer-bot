import praw
import io

token_file = io.open("creds/token.txt", "r")
token = token_file.readlines()
token_file.close()

if len(token) > 0:
    reddit = praw.Reddit(client_id=token[0],
                     client_secret=token[1],
                     user_agent='my user agent')
    print(reddit.user.me())