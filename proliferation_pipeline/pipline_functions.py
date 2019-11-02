import requests 
import json

import random

##################################################################################################
# Gets all the comment ids from a specific post
# 
# pass a post id such as "6uey5x" that corresponds to the reddit post you are intersted in
# full request looks like this: "https://api.pushshift.io/reddit/submission/comment_ids/6uey5x"
# Returns an array of comment ids that you can process with other function calls
# Comment ids come in chronological order
##################################################################################################
def post_comment_ids(post_id):
    post_comment_endpoint = "https://api.pushshift.io/reddit/submission/comment_ids/" #pushshift endpoint for querying comment_ids for a specific post

    full_url = post_comment_endpoint + post_id #adds post id to the url string

    request = requests.get(url=full_url)

    if request.status_code == 200:
        response = request.json()
        
    else:
        print("something went wrong")
        print("Tried to pull comment ids of: {}".format(post_id))
        print(request.status_code)


    return response['data'] 



##################################################################################################
# Gets all comment data from a list of comment ids
# 
# Inputs an array of comment_ids ["f2varzxq","f2vdegg"], re-formats them as a comma-deliminated string and feeds it as a parameter to the pushshift api
# 
# Requests with endpoint "https://api.pushshift.io/reddit/search/comment/" and parameter of the comma-deliminated string
##################################################################################################

def get_comment_data(post_id,comment_ids):
    search_comment_endpoint = "https://api.pushshift.io/reddit/search/comment/"

    #random_ids = random.sample(comment_ids, 20)
    
    csv_ids = ",".join(comment_ids[1:100]) #Only calling responses for the first 100 comments for now
       
    params = {
        "ids": csv_ids,
        "size": 500
    }
    request = requests.get(url=search_comment_endpoint, params=params)

    if request.status_code == 200:
        response = request.json()
        
    else:
        print("something went wrong")
        print("Tried to pull comment data from post: {}".format(post_id))
        print(request.status_code)

    return response['data']

def get_user_activity(author, created_at):
    search_comment_endpoint = "https://api.pushshift.io/reddit/search/comment/"
    search_post_endpoint = "https://api.pushshift.io/reddit/search/submission/"
    #activity = []

    params = {
        "author": author,
        "after": created_at,
        "size": 25 #max of 500, but we can boost it with a loop and an update to after alla scrape.py file
    }

    post_request = requests.get(url=search_post_endpoint, params=params)
    comment_request = requests.get(url=search_comment_endpoint, params=params)

    if post_request.status_code == 200:
        post_response = post_request.json()
        
    else:
        print("something went wrong")
        print("Tried to pull post activity from user: {}".format(author))
        print(post_request.status_code)

    if comment_request.status_code == 200:
        comment_response = comment_request.json()
        
    else:
        print("something went wrong")
        print("Tried to pull comment activity from user: {}".format(author))
        print(comment_request.status_code)    


    return [post_response['data'], comment_response['data']]