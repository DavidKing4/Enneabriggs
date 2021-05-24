import csv
import json
from math import ceil 
import praw
import requests
from tqdm import tqdm
# Warning file takes a long time to run 40+ hours
# Edit your praw.ini file to include your own credentials

def get_users(subreddit, file_name):
    url_base = "https://api.pushshift.io/reddit/search/submission/?"
    params = {
        "subreddit":subreddit,
        "size":100
    }
    users = dict()
    ids = []

    r = requests.get(f"https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&metadata=true&size=0")
    meta = json.loads(r.text)
    for i in tqdm(range(ceil(meta["metadata"]["total_results"]/100))):
        r = requests.get(url_base, params = params)
        try:
            j = json.loads(r.text)
            for post in j["data"]:
                if flair := post["author_flair_text"]:
                    users[post["author"]] = flair
                ids.append(post["id"])
        except json.decoder.JSONDecodeError:
            print(params)
            print(r.text)
        params["before"] = j["data"][-1]["created_utc"]
        if not j["data"]:
            break

    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in users.items():
            writer.writerow([key, value])

    ids.reverse()
    reddit = praw.Reddit()
    x = 0
    for id in tqdm(ids):
        x += 1
        post = reddit.submission(id)
        comments = post.comments
        comments.replace_more(limit=None)
        for comment in comments.list():
            if comment.author not in users:
                users[comment.author] = comment.author_flair_text
        if x % 1000 == 0:
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for key, value in users.items():
                    writer.writerow([key, value])

    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in users.items():
            writer.writerow([key, value])

if __name__ == "__main__":
    get_users(subreddit="mbti", file_name='Data\\mbti_.csv')
    get_users(subreddit="Enneagram", file_name="Data\\Enneagram_.csv")