from pipline_functions import get_post_comment_ids,get_posts_data,get_comments_data,get_user_posts,get_crosspost_ids,get_crossposts
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
    seed_post = get_posts_data([seed_id])[0]
    
    since = seed_post['created_utc']
    until = since + 604800
    post_ids = {}
    authors = {}
    
    post_ids[seed_id] = True
    
    
    proliferate(seed_post, post_ids, authors, since, until)


def proliferate(post, post_ids, author_ids, since, until):
    post_ids[post['id']] = True
    comment_ids = get_post_comment_ids(post['id'])
    comments = parse_comments(get_comments_data(post['id'], comment_ids), post['id'], post_ids)
    new_posts = []
    new_authors = []
    for comment in comments:
        post_ids[comment['id']] = True
        author = comment['author']
       
        if author not in author_ids or author_ids[author] == False:
            user_posts = get_user_posts(author, since, until)
            parsed_user_posts = parse_posts(user_posts, post_ids)
            new_posts = new_posts + parsed_user_posts
            author_ids[author] = True
            new_authors.append(author)
        else:
            continue

    # get crossposts
    crossposts = parse_posts(get_crossposts(post['full_link']), post_ids)
    new_posts = new_posts + crossposts

    db_push(cur, conn, new_authors, new_posts, comments)
    
    for new_post in new_posts:
        proliferate(new_post, post_ids, author_ids, since, until)

def parse_comments(comments_data, post_id, post_id_dict):
    parsed_comments = []
    if post_id in post_id_dict and post_id_dict[post_id] == True: #Check if we've already handled the post that these comments are coming from 
        nothing = "do nothing"
    elif len(comments_data) > 0: #If we haven't handled that post, let's check that there are comments to handle
        for comment in comments_data:
            
            comment_id = comment['id']
            if comment_id in post_id_dict and post_id_dict[comment_id] == True:
                continue
            parsed_comment = {
                'id': key_or_nah(comment, "id"),
                'author': key_or_nah(comment, "author"),
                'post_id': post_id,
                'body': key_or_nah(comment, "body"),
                'score': key_or_nah(comment, "score"),
                'created_utc': key_or_nah(comment, "created_utc"),
                'retrieved_on': key_or_nah(comment, "retreived_on"),
                'parent_id': key_or_nah(comment, "parent_id"),
                'stickied': key_or_nah(comment, "stickied"),
                'subreddit': key_or_nah(comment, "subreddit"),
                'permalink': key_or_nah(comment, "permalink")
            }

            parsed_comments.append(parsed_comment)
    
    return parsed_comments


def parse_posts(all_posts_data, post_id_dict):
    parsed_posts = []
    if len(all_posts_data) > 0:
        for post_data in all_posts_data:
            post_id = post_data['id']
            if post_id in post_id_dict and post_id_dict[post_id] == True:
                continue
   
            parsed_post = {
            "author": key_or_nah(post_data, "author"),
            "created_utc": key_or_nah(post_data, "created_utc"),
            "full_link": key_or_nah(post_data, "full_link"),
            "id": key_or_nah(post_data, "id"),
            "num_comments": key_or_nah(post_data, "num_comments"),
            "num_crossposts": key_or_nah(post_data, "num_crossposts"),
            "retrieved_on": key_or_nah(post_data, "retrieved_on"),
            "score": key_or_nah(post_data, "score"),
            "selftext": key_or_nah(post_data, "selftext"),
            "subreddit": key_or_nah(post_data, "subreddit"),
            "post_hint": key_or_nah(post_data, "post_hint"),
            "subreddit_subscribers": key_or_nah(post_data, "subreddit_subscribers"),
            "title": key_or_nah(post_data, "title"),
            "updated_utc": key_or_nah(post_data, "updated_utc"),
            "url": key_or_nah(post_data, "url")
            }
            

            parsed_posts.append(parsed_post)
            
    return parsed_posts


def key_or_nah(dictionary, key): #checks to see if a key exists in a dictionary. If it does, return its pair value. If not, return nothing
    if key in dictionary:
        return dictionary[key]
    else:
        return None

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
    