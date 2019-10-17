import json
import pandas as pd

all_posts = pd.DataFrame(columns=["author","author_fullname","created_utc","full_link","id","is_self","is_video","num_comments","num_crossposts","score","selftext","subreddit","title","url"])


with open("posts.txt") as f:
    posts_json = json.load(f)

for subreddit in posts_json:
    for post in posts_json[subreddit]: #Iterate through all the reddits, within them find an array
        try:
            all_posts = all_posts.append({
                "author": post["author"],
                "author_fullname": post["author_fullname"],
                "created_utc": post["created_utc"],
                "full_link": post["full_link"],
                "id": post["id"],
                "is_self": post["is_self"],
                "is_video": post["is_video"],
                "num_comments": post["num_comments"],
                "num_crossposts": post["num_crossposts"],
                "score": post["score"],
                "selftext": post["selftext"],
                "subreddit": post["subreddit"],
                "title": post["title"],
                "url": post["url"],
            }, ignore_index=True)
        except: #Needed when a user has deleted his or her account
            all_posts = all_posts.append({
                "author": "[deleted]",
                "author_fullname": "[deleted]",
                "created_utc": post["created_utc"],
                "full_link": post["full_link"],
                "id": post["id"],
                "is_self": post["is_self"],
                "is_video": post["is_video"],
                "num_comments": post["num_comments"],
                "num_crossposts": post["num_crossposts"],
                "score": post["score"],
                "selftext": "[deleted]",
                "subreddit": post["subreddit"],
                "title": post["title"],
                "url": post["url"],
            }, ignore_index=True)


all_posts.to_csv("posts.csv", index=False)
