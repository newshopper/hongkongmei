import datetime
import time
from scrape import scraper
import json
import random
import pandas as pd
import pprint
import csv



##############################################################
# Our initial script for retrieving submission data from Reddit
# using the pushshift.io api.
#
# This script returns all posts from a series of subreddits
# between two dates/
##############################################################










subreddits = ["hearthstone", "blizzard", "HongKong", "overwatch", "gaming"]

if __name__ == "__main__":
    # get 50 posts each from the above subreddits in the past 2 days
    submission_endpoint = "https://api.pushshift.io/reddit/search/submission/"
    start_time = datetime.datetime(2019,10,30,0,0,0).timestamp()
    end_time = datetime.datetime(2019,11,1,0,0,0).timestamp()
    posts = {
        "hearthstone": [],
        "blizzard": [],
        "HongKong": [],
        "overwatch": [],
        "gaming": []
    }
    subreddits = ["hearthstone", "blizzard", "HongKong", "overwatch", "gaming"]
    sample = []
    hearthstone_posts = scraper(submission_endpoint, subreddits[0], start_time, end_time, posts)
    # randomly select 50 posts
    hearthstone_sample = random.sample(hearthstone_posts["hearthstone"], 10)
    sample.extend(hearthstone_sample)
    blizzard_posts = scraper(submission_endpoint, subreddits[1], start_time, end_time, hearthstone_posts)
    blizzard_sample = random.sample(blizzard_posts["blizzard"], 10)
    sample.extend(blizzard_sample)
    hongkong_posts = scraper(submission_endpoint, subreddits[2], start_time, end_time, blizzard_posts)
    hongkong_samples = random.sample(hongkong_posts["HongKong"], 10)
    sample.extend(hongkong_samples)
    overwatch_posts = scraper(submission_endpoint, subreddits[3], start_time, end_time, hongkong_posts)
    overwatch_samples = random.sample(overwatch_posts["overwatch"], 10)
    sample.extend(overwatch_samples)
    gaming_posts = scraper(submission_endpoint, subreddits[4], start_time, end_time, overwatch_posts)
    gaming_samples = random.sample(gaming_posts["gaming"], 10)
    sample.extend(gaming_samples)
    # Now that we have 50 posts each of all the relevant subreddits, we have to pull out the title text and self text
    # from each of the posts and put them in a dataframe along with the post id.
    # iterate over the samples
    
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(sample)
    dataframe = pd.DataFrame(columns=['id', 'title', 'text'])
    for post in sample:
        post_id = post["id"]
        post_title = post["title"]
        if "selftext" in post:
            post_text = post["selftext"]
        else:
            post_text = ""
        dataframe = dataframe.append({'id': post_id, 'title': post_title, 'text': post_text}, ignore_index=True)
    
    # convert dataframe into CSV
    dataframe.to_csv("sample_posts.csv", index=False)