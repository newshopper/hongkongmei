from pipline_functions import post_comment_ids,get_comment_data,get_user_activity
import pandas as pd
import time
## Seed posts
# https://www.reddit.com/r/hearthstone/comments/dehdhm/blizzard_taiwan_deleted_hearthstone_grandmasters/  
# https://www.reddit.com/r/HongKong/comments/df2rz7/it_would_be_such_a_shame_if_mei_from_overwatch/ 






def main():

    blitzchung_seed_id = "dehdhm" #post id of our approximate first post about blitzchung 
    mei_seed_id = "df2rz7" #post id of our definite first post memeing mei

   

    comment_ids = post_comment_ids(blitzchung_seed_id)
    print("Number of comments: {}".format(len(comment_ids)))
    comment_data = get_comment_data(blitzchung_seed_id, comment_ids)

    authors = []
    for comment in comment_data:
        authors.append([comment["author"],comment["created_utc"]])
    
    post_activity_df = pd.DataFrame(columns=["type","author","title","text","id","created_utc","link"])
    comment_activity_df = pd.DataFrame(columns=["type", "author","body","id","created_utc","link"])
    for author in authors:
        time.sleep(10)
        print(author)
        activity = get_user_activity(author[0],author[1]) #return a list of all the user activity first element is post activity, second element is comment activity
        post_activity = activity[0]
        comment_activity = activity[1]
        
        for post in post_activity:
            post_activity_df = post_activity_df.append({
                "type": "post",
                "author": post["author"],
                "title": post["title"],
                "text": post["selftext"],
                "id": post["id"],
                "created_utc": post["created_utc"],
                "link": post["full_link"],
            }, ignore_index=True)
       
        for comment in comment_activity:
            
            comment_activity_df = comment_activity_df.append({
                "type": "comment",
                "author": comment["author"],
                "body": comment["body"],
                "id": comment["id"],
                "created_utc": comment["created_utc"],
                "link": "reddit.com" + comment["permalink"],
            }, ignore_index=True)
     
    post_activity_df.to_csv("post_activity.csv", index=False)
    comment_activity_df.to_csv("comment_activity.csv", index=False)
if __name__ == "__main__":
    main()