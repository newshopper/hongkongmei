from pipline_functions import get_posts_data,get_comments,get_user_posts,get_crosspost_ids,get_crossposts,get_crossposts_praw,parse_posts,parse_comments
from storage_functions import open_database,set_cursor,wipe_database,close_database
from storage_functions import create_tables #Wrapper function to create three tables
from storage_functions import db_push #Wrapper function to push reddit data to db
import pandas as pd
import time
import os
import sys
### Seed posts
## Three options for general seed
# First post about blizzard suspension to gain big traction in major subreddit: https://www.reddit.com/r/hearthstone/comments/dehdhm/blizzard_taiwan_deleted_hearthstone_grandmasters/   
# The original post that the above post is a crosspost of:  https://www.reddit.com/r/KotakuInAction/comments/degg4x/blizzard_taiwan_deleted_hearthstone_grandmasters/
# The first time the specific twitter link appeared on reddit: https://www.reddit.com/r/HongKong/comments/degek8/hearthstone_grandmasters_winners_interview_with/
# 
## There are even earlier posts regarding the stream itself. Since it's not specific to the controversy, we can keep things here 
#
## Mei seed
# https://www.reddit.com/r/HongKong/comments/df2rz7/it_would_be_such_a_shame_if_mei_from_overwatch/ 

 #######################################################################################
# Bring in environment variables to connect to aws rds db
#
# To set environment variables in windows, run the following command in command prompt:
# set [variable_name]=[variable_value] 
#######################################################################################

port = int(os.environ.get("port"))
username = os.environ.get("username")
password = os.environ.get("password")
endpoint = os.environ.get("endpoint")
dbname = os.environ.get("dbname")

#Set database connection
conn = open_database(dbname, username, password, endpoint, port)
cur = set_cursor(conn)



def main(write):
    # if we have chosen to overwrite the database then run the following commands
    if write == 'overwrite':
        wipe_database(cur) #wipe database to give ourselves a clear slate every time we run this seed script
        create_tables(cur,conn)

    
    blitzchung_seed_id = "degek8" #post id of our approximate first post about blitzchung 
    mei_seed_id = "df2rz7" #post id of our definite first post memeing mei

    
    # posts_data = get_posts_data([blitzchung_seed_id, mei_seed_id])
    # comment_ids = get_post_comment_ids(blitzchung_seed_id)
    # comments_data = get_comments_data(blitzchung_seed_id,comment_ids)
    # #posts_data = map(parse_post, posts_data)

   
    # created_utc = 1570435322
    # author = "williamthebastardd"


    initialize_pipeline(blitzchung_seed_id)
    
def initialize_pipeline(seed_id):
    print("Initializing pipeline ... feeding in seed post")
    
    post_ids = {} #establish dictionary to track processed posts
    author_ids = {} #establish dictionary to track new authors  
    post_queue = [] #queue of posts to process
    seed_post = get_posts_data([seed_id])[0] #Call data on first post
    parsed_seed_post = parse_posts([seed_post], post_ids)[0]

    #Create time window to track user interaction
    since = parsed_seed_post['created_utc'] 
    until = since + 172800 #604800 #One week (in seconds) after seed post was posted
    
    # db_push(cur, conn, new_authors, new_posts, comments) 
    
    post_queue.append(seed_post)
    
    
    proliferate(post_queue[0], post_queue, post_ids, author_ids, since, until)


def proliferate(post, post_queue, post_ids, author_ids, since, until):
    
    
    #tabulate new reddit info coming in
    new_posts = []
    new_authors = []

    post_author = post['author']
    if post_author not in author_ids: #Check if we've processed the author of the post
        post_author_posts = get_user_posts(post_author, since, until)
        parsed_post_author_posts = parse_posts(post_author_posts, post_ids)
        new_authors = new_authors + [post_author] 
        new_posts = new_posts + parsed_post_author_posts
        author_ids[post_author] = True #Indicate that we've pulled their activity
    
    comments = get_comments(post['id']) #get all comment data from post
    parsed_comments = parse_comments(comments, post['id'], post_ids) #parse returns to remove unecessary data
    
    for parsed_comment in parsed_comments:
        post_ids[parsed_comment['id']] = True #add the comment id so we don't reiterate over it
        parsed_comment_author = parsed_comment['author']
        if parsed_comment_author not in author_ids:
            author_posts = get_user_posts(parsed_comment_author, since, until) #get user activity from this new (previously unseen) user
            parsed_author_posts = parse_posts(author_posts, post_ids)
            new_authors = new_authors + [parsed_comment_author] 
            new_posts = new_posts + parsed_author_posts
            author_ids[parsed_comment_author] = True
    

    db_push(cur, conn, new_authors, [post], parsed_comments) #push the post, it's comments and all participating authors to the db


    post_ids[post['id']] = True #All comments, crossposts and associated user data has been processed

    # get crossposts
    crossposts = get_crossposts_praw(post['id'])
    parsed_crossposts = parse_posts(crossposts, post_ids)
    
    new_posts = new_posts + parsed_crossposts

    # # add new posts to the queue
   
    if len(post_queue) > 0:
        post_queue.pop(0)
    post_queue = post_queue + new_posts
  
    proliferate(post_queue[0], post_queue, post_ids, author_ids, since, until)
    
   



if __name__ == "__main__":
    correct_input = False
    try: 
        write = sys.argv[1] 
        if write == "overwrite" or write == "update":
            correct_input = True
        else:
            print("Invalid argument") 
            print("'overwrite' to wipe database and start over. 'update' to pick up where you left off.")
            sys.exit()
    except:
        print("Missing argument after python script")
        print("'overwrite' to wipe database and start over. 'update' to pick up where you left off.")
        sys.exit()

    if correct_input:
        main(write)
    