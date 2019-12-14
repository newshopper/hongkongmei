import requests 
import json
import sys
import random
import os
import praw

##################################################################################################
# Gets Reddit credentials from environment variables
reddit_username = os.environ.get('reddit_username')
reddit_pass = os.environ.get('reddit_password')
reddit_client_id = os.environ.get('reddit_client_id')
reddit_client_secret = os.environ.get('reddit_client_secret')
reddit_user_agent = os.environ.get('reddit_user_agent')

reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_client_secret, password=reddit_pass,
                     user_agent=reddit_user_agent, username=reddit_username)


##################################################################################################

##################################################################################################
# Gets all the comment ids from a specific post
# 
# pass a post id such as "6uey5x" that corresponds to the reddit post you are intersted in
#
# full request looks like this: "https://api.pushshift.io/reddit/submission/comment_ids/6uey5x"
# Returns an array of comment ids that you can process with other function calls
# Comment ids come in chronological order
##################################################################################################
def get_post_comment_ids(post_id):
    print(f"Calling get_post_comment_ids method on post: {post_id}")
    
    post_comment_endpoint = "https://api.pushshift.io/reddit/submission/comment_ids/" #pushshift endpoint for querying comment_ids for a specific post

    full_url = post_comment_endpoint + post_id #adds post id to the url string

    request = requests.get(url=full_url)

    if request.status_code == 200:
        response = request.json()
         
    else:
        print("something went wrong")
        print("Tried to pull comment ids of: {}".format(post_id))
        print(f'status code: {request.status_code}')
        sys.exit()

    return response['data']
    

################################################################################################
# Get post data using list of post id strings
# pass a list of unique id strings such as ["6uey5x","degek8","df2rz7"] that corresponds to the reddit post you are intersted in
# 
# Use https://api.pushshift.io/reddit/search/submission/ as endpoint and pass the list of ids as a parameter
#
# Returns a list of all the post information 
###############################################################################################
def get_posts_data(post_ids):
    print(f"Calling get_post_data method on posts: {post_ids}")
    
    search_post_endpoint = "https://api.pushshift.io/reddit/search/submission/"    

    print(f'Total posts to fetch: {len(post_ids)}')
    

    num_returned_posts = 0

    all_post_data = []

    while num_returned_posts < len(post_ids): #loop until we have returned data for all posts
        if len(post_ids) - num_returned_posts < 500: #if there is less than 500 posts left to return, return what is left to return
            num_incoming_posts =  len(post_ids) - num_returned_posts
        else:
            num_incoming_posts = 500 #else return 500 comments as we build towards returning all posts

        print(f'Fetching posts: {num_returned_posts} to {num_returned_posts + num_incoming_posts}')

        
        #Isolate the specific comment ids that we are fetching now. We can only fetch a max of 500 at a time
        fetching_posts = post_ids[num_returned_posts:num_returned_posts+num_incoming_posts]
        
        params = {
            'ids': fetching_posts,
            'size': 500
        }
        num_returned_posts = num_returned_posts + num_incoming_posts #increment our returned comments for the while loop

        request = requests.get(url=search_post_endpoint, params=params)

        if request.status_code == 200:
            response = request.json()
            all_post_data = all_post_data + response['data']
        
        else:
            print("something went wrong")
            print(f"Tried to pull post data from posts: {fetching_posts}")
            print(f'status code: {request.status_code}')
            sys.exit()     

    return all_post_data
    

################################################################################################
# Get crosspost ids from the given URL. The URL passed is the full_link passed from the
# parent post.
#
# Returns a list of post ids
################################################################################################
def get_crosspost_ids(url):
    '''
    Get crosspost ids from the given URL
    Returns a list of post ids
    '''
    # modify the URL to get the duplicates URL
    dupli_url = url.replace('comments', 'duplicates')
    # add .json to the end of dupli_url
    dupli_url = dupli_url + '.json'
    #print(dupli_url)
    
    headers = {
        "User-agent": "py_script:personal_use_scrip:v0 (by /u/beautifulalphbetsoup)"
    }
    
    # make a GET request for dupli_url and read the JSON data
    request = requests.get(dupli_url, headers=headers)
    
    crosspost_ids = []
    # print(request.status_code)
    if request.status_code == 200:
        results = request.json()
        # read the second element of the array
        crossposts_dict = results[1]
        crossposts_array = crossposts_dict['data']['children']
        for crosspost in crossposts_array:
            crosspost_data = crosspost['data']
            crosspost_id = crosspost_data['id']
            crosspost_ids.append(crosspost_id)
    else:
        print("something went wrong")
        print(f"Tried to pull crosspost data from url: {url}")
        print(f'status code: {request.status_code}')
        sys.exit()  

    return crosspost_ids

################################################################################################

################################################################################################
def get_crossposts(url):
    '''
    Get crossposts from the given URL. This method gets all the crosspost ids first and then calls
    get_posts_data() to retrieve the content of the posts
    '''
    crosspost_ids = get_crosspost_ids(url)
    crossposts = get_posts_data(crosspost_ids)
    return crossposts

################################################################################################

################################################################################################
def get_crossposts_praw(post_id):
    '''
    Get crossposts using the praw library. It takes the original post_id as input.
    '''
    submission = reddit.submission(id=post_id)
    crossposts = []
    for duplicate in submission.duplicates():
        
        parsed_post = {
            "author": duplicate.author,
            "created_utc": duplicate.created_utc,
            "id": duplicate.id,
            "num_comments": duplicate.num_comments,
            "num_crossposts": duplicate.num_crossposts,
            "score": duplicate.score,
            "selftext": duplicate.selftext,
            "subreddit": duplicate.subreddit,
            "post_hint": duplicate.post_hint,
            "subreddit_subscribers": duplicate.subreddit_subscribers,
            "title": duplicate.title,
            "url": duplicate.url
            }
        crossposts.append(parsed_post)
    return crossposts

##################################################################################################
# Gets all comment data from a list of comment ids 
# 
# Inputs an array of comment_ids ["f2varzxq","f2vdegg"], re-formats them as a comma-deliminated 
# string and feeds it as a parameter to the pushshift api 
# 
# Requests with endpoint "https://api.pushshift.io/reddit/search/comment/" and parameter of 
# the comma-deliminated string 'ids'. 
# 
# Note: There are some limitations with the number of comments we can access at a time. So, we have
# to run a while loop to return all of them
##################################################################################################

def get_comments_data(post_id,comment_ids):
    '''
    Gets all comment data from a list of comment ids 
    Inputs an array of comment_ids ["f2varzxq","f2vdegg"], re-formats them as a comma-deliminated 
    string and feeds it as a parameter to the pushshift api 
    Requests with endpoint "https://api.pushshift.io/reddit/search/comment/" and parameter of 
    the comma-deliminated string 'ids'. 
    Note: There are some limitations with the number of comments we can access at a time. So, we have
    to run a while loop to return all of them
    '''
    print("Calling get_comments_data method")
    
    search_comment_endpoint = "https://api.pushshift.io/reddit/search/comment/"

    print(f'Total comments to fetch: {len(comment_ids)}')

    returned_comments = 0

    all_comment_data = [] #the list where we will store all comment data

    while returned_comments < len(comment_ids): #loop until we have returned all comment data
        if len(comment_ids) - returned_comments < 500: #if there is less than 500 comments left to return, return what is left to return
            incoming_comments =  len(comment_ids) - returned_comments 
        else:
            incoming_comments = 500 #else return 500 comments as we build towards returning all comments

        
        print(f'Fetching comments: {returned_comments} to {returned_comments + incoming_comments}')
        
        #Isolate the specific comment ids that we are fetching now. We can only fetch a max of 500 at a time
        fetching_comments = comment_ids[returned_comments:returned_comments+incoming_comments]
        
        csv_ids = ",".join(fetching_comments) 
       
        params = {
            "ids": csv_ids,
            "size": 500
         }
        request = requests.get(url=search_comment_endpoint, params=params)

        if request.status_code == 200:
            response = request.json()
            all_comment_data = all_comment_data + response['data']
        
        else:
            print("something went wrong")
            print("Tried to pull comment data from post: {}".format(post_id))
            print(f'Tried to pull comments from indices {returned_comments} to {returned_comments + incoming_comments}')
            print(f'status code: {request.status_code}')
            sys.exit()
        
        
        returned_comments = returned_comments + incoming_comments #increment our returned comments for the while loop
    return all_comment_data # response['data']


######################################################################################
# Get posts from user between a specific epoch (utc) time frame
# Pass author, a start utc and an end utc
# 
# We decided to limit our time frame to 7 days, or 604800 seconds
# Uses the submission search endpoint: "https://api.pushshift.io/reddit/search/submission/"
# 
# This method is used in the main script to find posts by users after interaction on a previous post
# Returns a list of post ids 
######################################################################################
def get_user_posts(author, since, until):
    '''
    Get posts from user between a specific epoch (utc) time frame
    Pass author, a start utc and an end utc

    We decided to limit our time frame to 7 days, or 604800 seconds
    Uses the submission search endpoint: "https://api.pushshift.io/reddit/search/submission/"

    This method is used in the main script to find posts by users after interaction on a previous post
    Returns a list of post ids 
    '''
    search_post_endpoint = "https://api.pushshift.io/reddit/search/submission/"
    all_post_data = []

    while True:

        params = {
            "author": author,
            "after": since,
            "before": until,
            "size": 500 #max of 500, but we can boost it with a loop and an update to after alla scrape.py file
        }

        request = requests.get(url=search_post_endpoint, params=params)
        if request.status_code == 200:
            response = request.json()
            all_post_data = all_post_data + response['data']
            if len(response['data']) < 500:
                break
            else: 
                since = response['data'][-1]['created_utc']  
        else:
            print("something went wrong")
            print("Tried to pull post activity from user: {}".format(author))
            print(f'status code: {request.status_code}')

    return all_post_data



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