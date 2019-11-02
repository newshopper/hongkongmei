from pipline_functions import post_comment_ids,get_post_data,get_comment_data,get_user_activity
from storage_functions import open_database,set_cursor,wipe_database,close_database
from storage_functions import create_posts_table, create_comments_table, create_users_table
from storage_functions import store_post,store_comment,store_user
import pandas as pd
import time
## Seed posts
# https://www.reddit.com/r/hearthstone/comments/dehdhm/blizzard_taiwan_deleted_hearthstone_grandmasters/  
# https://www.reddit.com/r/HongKong/comments/df2rz7/it_would_be_such_a_shame_if_mei_from_overwatch/ 






def main():

    # Three dictionaries representatives of what we will likely store in our data base 
    # In our final version, we will limit posts by whether or not they include stuff from hong kong

    #Posts have a key of the post id. This is unique to each post. Inside we will store author, num_comments, etc.
    #We can check if a post has been processed already by checking if its id exists as a key to this dictionary
    posts = {} 
    #Comments have a key of the comment id. This is unique to each comment. Comments will also store the post id they are related to and the user id of the user that made them
    comments = {}
    #Users have a key of the user id. This is unique to each user. Users will not need foreign keys (probably)
    users = {}



    conn = open_database("hongkongmei","postgres","atclassof2021")
    cur = set_cursor(conn)

    
    wipe_database(cur) #wipe database to give ourselves a clear slate every time we run this seed script

    create_posts_table(cur,conn)
    create_comments_table(cur,conn)


    blitzchung_seed_id = "dehdhm" #post id of our approximate first post about blitzchung 
    mei_seed_id = "df2rz7" #post id of our definite first post memeing mei


    post = get_post_data(blitzchung_seed_id)

    #print(post)

    # comment_ids = post_comment_ids(blitzchung_seed_id)
    # print("Number of comments: {}".format(len(comment_ids)))
    # comment_data = get_comment_data(blitzchung_seed_id, comment_ids)
    # print(comment_data[4])
    # authors = []
    # for comment in comment_data:
    #     authors.append([comment["author"],comment["created_utc"]])
    
    # post_activity_df = pd.DataFrame(columns=["type","author","title","text","id","created_utc","link"])
    # comment_activity_df = pd.DataFrame(columns=["type", "author","body","id","created_utc","link"])
    # for author in authors:
    #     time.sleep(10)
    #     print(author)
    #     activity = get_user_activity(author[0],author[1]) #return a list of all the user activity first element is post activity, second element is comment activity
    #     post_activity = activity[0]
    #     comment_activity = activity[1]
        
    #     for post in post_activity:
    #         post_activity_df = post_activity_df.append({
    #             "type": "post",
    #             "author": post["author"],
    #             "title": post["title"],
    #             "text": post["selftext"],
    #             "id": post["id"],
    #             "created_utc": post["created_utc"],
    #             "link": post["full_link"],
    #         }, ignore_index=True)
       
    #     for comment in comment_activity:
            
    #         comment_activity_df = comment_activity_df.append({
    #             "type": "comment",
    #             "author": comment["author"],
    #             "body": comment["body"],
    #             "id": comment["id"],
    #             "created_utc": comment["created_utc"],
    #             "link": "reddit.com" + comment["permalink"],
    #         }, ignore_index=True)
     
    # post_activity_df.to_csv("post_activity.csv", index=False)
    # comment_activity_df.to_csv("comment_activity.csv", index=False)
if __name__ == "__main__":
    main()