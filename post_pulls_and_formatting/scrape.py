import time
import json
import requests

import itertools


post_id = 0
# We want to collect:
## Post id (maybe post url, also)
## Post time
## Text
## upvotes (score)
## poster username
## Number of comments
## Any links to media (maybe even save the links in another folder)

#########################################################################################
## Method takes a subreddit and returns all posts from a subreddit since a certain time
## interval. Stores post information in a json format
#########################################################################################

def scraper(endpoint, subreddit, time_start, time_end, posts):
    
    params = {
        "subreddit": subreddit,
        "size": 500,
        "after": int(time_start),
    }

    request = requests.get(url=endpoint, params=params)
    if request.status_code == 200:
        response = request.json()
        if len(response['data']) == 0:
            #print(posts)
            return posts
        for submission in response['data']:
            if submission["created_utc"] > time_end: #stop getting posts if we cross our time threshold. Old run is 1570824407, new run in midnight Sunday night
                return posts
            post_id = submission['id']
            print(post_id)
            time_start = submission['created_utc'] #constantly updates the new startime with the most recent processed post. The most recent processed post from the 500 returned becomes the new staritng po
            posts[subreddit].append(submission)
        
    else:
        print("something went wrong")
        print("Last post: {}".format(post_id))
        print(request.status_code)
    print("break")
    return scraper(endpoint,subreddit,time_start+1,time_end,posts)
    #Once 500 entries have been returned, take the most recent post time and pass it as the
    # New start time for scraper, for the next 500 posts.    
    #scraper(endpoint, subreddit, time_start, time_end)
    