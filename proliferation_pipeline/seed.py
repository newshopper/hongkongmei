from pipline_functions import get_post_comment_ids,get_posts_data,get_comments_data,get_user_posts,get_crosspost_ids,get_crossposts, parse_posts, parse_comments
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

post_queue = []

def main(write):
    # if we have chosen to overwrite the database then run the following commands
    if write == 'overwrite':
        wipe_database(cur) #wipe database to give ourselves a clear slate every time we run this seed script
        create_tables(cur,conn)

    
    blitzchung_seed_id = "degek8" #post id of our approximate first post about blitzchung 
    mei_seed_id = "df2rz7" #post id of our definite first post memeing mei

    
    # test = get_crossposts("df2rz7")
    
    # for item in test:
    #     print(item['author'])
    #     print(item['subreddit'])
    #     print(item['title'])
    #     print("")

    crossposts = get_crossposts("https://www.reddit.com/r/HongKong/comments/df2rz7/it_would_be_such_a_shame_if_mei_from_overwatch/")

    print(crossposts)
    # posts_data = get_posts_data([blitzchung_seed_id, mei_seed_id])
    # comment_ids = get_post_comment_ids(blitzchung_seed_id)
    # comments_data = get_comments_data(blitzchung_seed_id,comment_ids)
    # #posts_data = map(parse_post, posts_data)

   
    # created_utc = 1570435322
    # author = "williamthebastardd"


    #initialize_pipeline(blitzchung_seed_id)
    
def initialize_pipeline(seed_id):
    print("Initializing pipeline ... feeding in seed post")
    seed_post = get_posts_data([seed_id])[0]
    
    since = seed_post['created_utc']
    until = since + 604800
    post_ids = {}
    authors = {}
    
    post_ids[seed_id] = True
    
    global post_queue
    post_queue.append(seed_post)
    proliferate(post_queue[0], post_ids, authors, since, until)


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

    global post_queue
    if len(post_queue) > 0:
        # remove the first element
        post_queue.pop(0)
    
    post_queue = post_queue + new_posts

    db_push(cur, conn, new_authors, new_posts, comments)
    
    proliferate(post_queue[0], post_ids, author_ids, since, until)
    
    # for new_post in new_posts:
    #     proliferate(new_post, post_ids, author_ids, since, until)



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
    