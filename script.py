
import datetime
import time
from reddit_api_info import client_id,client_secret,user_agent,username,password
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

    #Set the scraper start time as the beginning of the day before the blizzard announcement
    start_time = datetime.datetime(2019,10,7,0,0,0).timestamp() #converts to epoch time
    
    #Set the scraper end time as the current epoch time 
    current_time = time.time() 

    hearthstone_posts = scraper(submission_endpoint, subreddits[0], start_time, current_time, posts)
    blizzard_posts = scraper(submission_endpoint, subreddits[1], start_time, current_time, hearthstone_posts)
    HongKong_posts = scraper(submission_endpoint, subreddits[2], start_time, current_time, blizzard_posts) 
    overwatch_posts = scraper(submission_endpoint, subreddits[3], start_time, current_time, HongKong_posts)
    all_posts = scraper(submission_endpoint, subreddits[4], start_time, current_time, overwatch_posts)

    with open("posts.txt", 'w') as output:
            json.dump(all_posts,output)


if __name__ == "__main__":
    main()