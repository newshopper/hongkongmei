from pipline_functions import get_posts_data,get_comments,get_user_posts,get_crosspost_ids,get_crossposts, enqueue_post_ids
from pipline_functions import get_crossposts_praw,parse_posts,parse_comments, get_relevant_posts, get_relevant_comments
from pipline_functions import is_post_relevant
from storage_functions import open_database,set_cursor,wipe_database,close_database
from storage_functions import create_tables #Wrapper function to create three tables
from storage_functions import db_push #Wrapper function to push reddit data to db
import pandas as pd
import time
import os
import sys

##################################################################
# Programming TODO:
#
# Create checkpoint system for queue loop: saving queue, post_ids and author_ids
# # # Store dict/json file in checkpoint folder. Specify file in python seed.py update /checkpoint/filename.json
#
# Fix various coding issues
# # # Speed up user_activity function  
# # # # # # Limit sleep time? Contact Pushshift? Post in r/redditdev?
# # # Figure out why we are returning posts outside our date range
# # # Fix crossposts count in post data 
#
# Reorganize pipeline code
# # # Strip seed.py to basics and move pipeline functions
# # # Eliminate praw function
# # # Too many things in pipeline functions. 
# # # # # # Split between pipeline queueing and data calls 
# 
# Comment code
# # # Descriptions for each function 
# # # step by step description for seed.py
#
# Clean up repo?
# # # Which files are necessary? Remove OCR stuff? 
#
# Write readme
# # # Remember to credit shuai
# # # Repo description and how to use it 
# # # # # # i.e. Step 1: Set up DB and environment variables Step2: hkpostfilter_test.py, Step 3: ....
# # # Add function descriptions
################################################################













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
    
    #proliferate(post_queue[0], post_queue, post_ids, author_ids, since, until, 0)
    
    seed_post,post_queue,post_ids,author_ids, since, until = initialize_pipeline(blitzchung_seed_id)
    count = 0
    while post_queue:
        post = post_queue.pop(0)
        print(f"Popping off post: {post['id']}")
        post_queue, post_ids, author_ids, since, until, count = proliferate(post, post_queue, post_ids, author_ids, since, until, count)
        
    



    
def initialize_pipeline(seed_id):
    print("Initializing pipeline ... feeding in seed post")
    
    post_ids = {} #establish dictionary to track queued and processed posts. Key is the post id. "False" means the post has been queued, but not processed. "True" means the post has been processed
    author_ids = {} #establish dictionary to track new authors  
    post_queue = [] #queue of posts to process
    seed_post = get_posts_data([seed_id])[0] #Call data on first post
    parsed_seed_post = parse_posts([seed_post], post_ids)[0]

    #Create time window to track user interaction
    since = parsed_seed_post['created_utc'] 
    until = since + 259200 #604800 #One week (in seconds) after seed post was posted

    post_ids[parsed_seed_post['id']] = False
    post_queue.append(parsed_seed_post)
    
    return seed_post,post_queue,post_ids,author_ids, since, until

def proliferate(post, post_queue, post_ids, author_ids, since, until, count):
    '''
    Handles the actions for proliferation of posts. Fetches comments of a post, the users
    associated with the comments and their posts. Only those posts are processed whose title/text
    are relevant to the Hong Kong protests. Comments are also similarly processed based on relevance.
    '''
    count = count + 1
    # if count > 4:
    #     print(post_queue)
    #     print(post_ids)
    #     sys.exit()


    prediction = is_post_relevant(post)
    # Process the post only if it is relevant to the Hong Kong protests
    if prediction == True and post_ids[post['id']] != True:
        #tabulate new reddit info coming in
        #new_posts = []
        new_authors = []

        post_author = post['author']
        if post_author not in author_ids: #Check if we've processed the author of the post (the OP)
            post_author_posts = get_user_posts(post_author, since, until)
            parsed_post_author_posts = parse_posts(post_author_posts, post_ids) #cleans up post data and only returns new posts (that are not already in the queue or haven't been processed)
            post_queue = post_queue + parsed_post_author_posts #add previously unseen posts from author to queue
            post_ids = enqueue_post_ids(parsed_post_author_posts, post_ids) #update post_ids to show the new posts from the author are now in the queue
            
            #new_posts = new_posts + parsed_post_author_posts
            new_authors = new_authors + [post_author] 
            author_ids[post_author] = True #Indicate that we've pulled their activity
        
        comments = get_comments(post['id']) #get all comment data from post
        parsed_comments = parse_comments(comments, post['id'], post_ids) #parse returns to remove unecessary data
        relevant_comments = get_relevant_comments(parsed_comments) # get comments relevant to the HK protests

        for parsed_comment in relevant_comments:
            post_ids[parsed_comment['id']] = True #add the comment id so we don't reiterate over it
            parsed_comment_author = parsed_comment['author']
            if parsed_comment_author not in author_ids:
                author_posts = get_user_posts(parsed_comment_author, since, until) #get user activity from this new (previously unseen) user
                parsed_author_posts = parse_posts(author_posts, post_ids)
                post_queue = post_queue + parsed_author_posts 
                post_ids = enqueue_post_ids(parsed_author_posts, post_ids)
                
                #new_posts = new_posts + parsed_author_posts
                new_authors = new_authors + [parsed_comment_author]
                author_ids[parsed_comment_author] = True

        #push the post, its comments and all participating authors to the db
        db_push(cur, conn, new_authors, [post], relevant_comments) 


        post_ids[post['id']] = True #All comments, crossposts and associated user data has been processed

        # get crossposts
        crossposts = get_crossposts(post['full_link'])
        # crossposts = get_crossposts_praw(post['id'])
        parsed_crossposts = parse_posts(crossposts, post_ids)
        post_queue = post_queue + parsed_crossposts
        post_ids = enqueue_post_ids(parsed_crossposts, post_ids)

        #new_posts = new_posts + parsed_crossposts
        
        
        # # add new posts to the queue
        #post_queue = post_queue + new_posts
        print([x['id'] for x in post_queue])
        # remove processed post from the queue
        #if len(post_queue) > 0:
            #post_queue.pop(0)
        #proliferate(post_queue[0], post_queue, post_ids, author_ids, since, until, count)
        return post_queue, post_ids, author_ids, since, until, count #return updated queue 
    else:
        post_ids[post['id']] = True
        #print(f"Not relevent: {post['id']}")
        #post_queue.pop(0)
        #if len(post_queue) > 0:
        #proliferate(post_queue[0], post_queue, post_ids, author_ids, since, until, count)
        return post_queue, post_ids, author_ids, since, until, count #return updated queue

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
    