
import datetime
import time
from scrape import scraper
import json
#subreddits to crawl:
## https://www.reddit.com/r/hearthstone/
## https://www.reddit.com/r/blizzard/
## https://www.reddit.com/r/HongKong/
## https://www.reddit.com/r/overwatch
## https://www.reddit.com/r/gaming


#Because reddit removed the ability to search by timestamp from it's api, we will be using the
# Pushshift api developed by (Jason Baumgartner)[https://twitter.com/jasonbaumgartne?lang=en]

subreddits = ["hearthstone", "blizzard", "HongKong", "overwatch", "gaming"]

def main():
   #create an empty json file to fill with post information
    posts = {
        "hearthstone": [],
        "blizzard": [],
        "HongKong": [],
        "overwatch": [],
        "gaming": []
    }

    #api endpoint to 
    submission_endpoint = "https://api.pushshift.io/reddit/search/submission/"

    #Set the scraper start time as the beginning of two days before the blizzard announcement
    start_time = datetime.datetime(2019,10,7,0,0,0).timestamp() #converts to epoch time

    #When the most recent time to get posts
    #end_time = 1570824407 #Timestamp of the last post we got when we first pulled the data
    end_time = datetime.datetime(2019,10,12,0,0,0).timestamp() #Get the posts through Friday Night THIS IS A NEW RUN

    

    #Calls the scaper function to contiously build up a json file with the posts returned from each subreddit
    #Full json object is realized with the final scraper method return into all_posts
    hearthstone_posts = scraper(submission_endpoint, subreddits[0], start_time, end_time, posts)
    blizzard_posts = scraper(submission_endpoint, subreddits[1], start_time, end_time, hearthstone_posts)
    HongKong_posts = scraper(submission_endpoint, subreddits[2], start_time, end_time, blizzard_posts) 
    overwatch_posts = scraper(submission_endpoint, subreddits[3], start_time, end_time, HongKong_posts)
    all_posts = scraper(submission_endpoint, subreddits[4], start_time, end_time, overwatch_posts)

    #Save all_posts
    with open("posts/all_posts_new.txt", 'w') as output:
            json.dump(all_posts,output)


if __name__ == "__main__":
    main()