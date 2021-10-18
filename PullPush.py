import csv
import datetime as dt
import json
from math import ceil
import praw
import requests
import time
from tqdm import tqdm

# Warning file takes a long time to run 40+ hours
# Edit your praw.ini file to include your own credentials


class UserGetter:
    def __init__(self, url_base=None, params=None, users=dict()):
        self.url_base = (
            url_base
            if url_base
            else "https://api.pushshift.io/reddit/search/submission/?"
        )
        self.params = params if params else {"size": 100, "sort": "desc"}
        self.users = users

    def get_users(self, subreddit, file_name, after_date=None):
        if after_date:
            assert isinstance(after_date, dt.date), "'after' must be of type date"
            if isinstance(after_date, dt.datetime):
                after_date = after_date.date()
            days = (dt.date.today() - after_date).days
            after = f"&after={days}d"
            self.params["after"] = f"{days}d"
        else:
            after = ""
        self.params["subreddit"] = subreddit
        users = self.users
        ids = []
        r = requests.get(
            f"{self.url_base}subreddit={subreddit}&metadata=true&size=0{after}"
        )
        meta = json.loads(r.text)
        for i in tqdm(range(ceil(meta["metadata"]["total_results"] / 100))):
            r = requests.get(self.url_base, params=self.params)
            if r.status_code == 429:
                print("\ntoo many requests, retrying in 1s...")
                print(self.params)
                print(r.text)
                time.sleep(1)
            r = requests.get(self.url_base, params=self.params)
            try:
                j = json.loads(r.text)
                for post in j["data"]:
                    if flair := post["author_flair_text"]:
                        users[post["author"]] = flair
                    ids.append(post["id"])
            except json.decoder.JSONDecodeError:
                print(self.params)
                print(r.text)
            try:
                self.params["before"] = j["data"][-1]["created_utc"]
            except IndexError:
                print(self.params)
                print(r.text)
                return
            if not j["data"]:
                break
        with open(file_name, "w", newline="", encoding="utf-8") as file:
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
                with open(file_name, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for key, value in users.items():
                        writer.writerow([key, value])
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for key, value in users.items():
                writer.writerow([key, value])
        self.users = users
        return users

    def update(subreddit, file_name, last_post_date):
        assert isinstance(
            last_post_date, dt.date
        ), "Date of last post must be Datetime or Date"
        self.days = (dt.date.today() - after).days
        return self.get_users(subreddit, file_name)


if __name__ == "__main__":
    usergetter = UserGetter()
    usergetter.get_users(subreddit="mbti", file_name="Data\\mbti_.csv")
    usergetter.get_users(subreddit="Enneagram", file_name="Data\\Enneagram_.csv")
