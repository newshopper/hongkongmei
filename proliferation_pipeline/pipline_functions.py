import requests 
import json
import sys
import random
import os
import praw
import time
import psycopg2
from hkpostfilter_test import predict

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


# Endpoint constants
CONST_COMMENT_ID_EP = "https://api.pushshift.io/reddit/submission/comment_ids/"
CONST_SEARCH_COMMENT_EP = "https://api.pushshift.io/reddit/search/comment/"
CONST_SEARCH_POST_EP = "https://api.pushshift.io/reddit/search/submission/"

# JSON Keys
CONST_AUTHOR = "author"
CONST_CREATED_UTC = "created_utc"
CONST_ID = "id"
CONST_NUMCOMMENTS = "num_comments"
CONST_NUMCROSSPOSTS = "num_crossposts"
CONST_SCORE = "score"
CONST_SELFTEXT = "selftext"
CONST_SUBREDDIT = "subreddit"
CONST_POSTHINT = "post_hint"
CONST_SUBREDDIT_SUBSCRIBERS = "subreddit_subscribers"
CONST_TITLE = "title"
CONST_FULL_LINK = "full_link"
CONST_RETRIEVED_ON = "retrieved_on"
CONST_URL = "url"
CONST_UPDATED_UTC = "updated_utc"
CONST_POST_ID = "post_id"
CONST_BODY = "body"
CONST_PARENT_ID = "parent_id"
CONST_PERMALINK = "permalink"
CONST_STICKIED = "stickied"
##################################################################################################  

################################################################################################
# Get post data using list of post id strings
# pass a list of unique id strings such as ["6uey5x","degek8","df2rz7"] that corresponds to the reddit post you are intersted in
# 
# Use https://api.pushshift.io/reddit/search/submission/ as endpoint and pass the list of ids as a parameter
#
# Returns a list of all the post information 
###############################################################################################
def get_posts_data(post_ids):
    print(f"Calling get_post_data method") #on posts: {post_ids}")   

    #print(f'Total posts to fetch: {len(post_ids)}')
    

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

        request = requests.get(url=CONST_SEARCH_POST_EP, params=params)

        if request.status_code == 200:
            response = request.json()
            all_post_data = all_post_data + response['data']
        elif request.status_code == 429:
            print("Rate limit exceeded. Sleeping for 5 sec")
            time.sleep(5)
            all_posts_data = get_posts_data(post_ids)
        else:
            print("something went wrong")
            print(f"Tried to pull post data from posts: {fetching_posts}")
            print(f'status code: {request.status_code}')
            #sys.exit()     

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
        #sys.exit()  

    return crosspost_ids

################################################################################################
# Get crossposts from the given URL. This method gets all the crosspost ids first and then calls
# get_posts_data() to retrieve the content of the posts
################################################################################################
def get_crossposts(url):
    '''
    Get crossposts from the given URL. This method gets all the crosspost ids first and then calls
    get_posts_data() to retrieve the content of the posts
    '''
    print(f'Fetching crossposts for: {url}')
    crosspost_ids = get_crosspost_ids(url)
    crossposts = get_posts_data(crosspost_ids)
    print(f'{len(crossposts)} crossposts fetched')
    return crossposts

################################################################################################
# Get crossposts using the praw library. It takes the original post_id as input.
################################################################################################
def get_crossposts_praw(post_id):
    '''
    Get crossposts using the praw library. It takes the original post_id as input.
    '''
    submission = reddit.submission(id=post_id)
    crossposts = []
    try:
        for duplicate in submission.duplicates():
            print('Processing crossposts')
            print(type(duplicate.created_utc))
            # if duplicate.created_utc < 1570435322 or duplicate.created_utc > 1570438922:
            #     continue
            parsed_post = {
                CONST_AUTHOR: duplicate.author,
                CONST_CREATED_UTC: duplicate.created_utc,
                CONST_ID: duplicate.id,
                CONST_NUMCOMMENTS: duplicate.num_comments,
                CONST_NUMCROSSPOSTS: duplicate.num_crossposts,
                CONST_SCORE: duplicate.score,
                CONST_SELFTEXT: duplicate.selftext,
                CONST_SUBREDDIT: duplicate.subreddit,
                CONST_POSTHINT: duplicate.post_hint,
                CONST_SUBREDDIT_SUBSCRIBERS: duplicate.subreddit_subscribers,
                CONST_TITLE: duplicate.title,
                CONST_URL: duplicate.url
                }
            crossposts.append(parsed_post)
    except:
        print(f"Error getting crossposts of post {post_id}")
        print("Moving on")
  
    return crossposts

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
    '''
    Gets all the comment ids from a specific post.
    Returns an array of comment ids in chronological order that you can process
    with other function calls.
    '''
    print(f"Calling get_post_comment_ids method on post: {post_id}")
    
    post_comment_endpoint = CONST_COMMENT_ID_EP #pushshift endpoint for querying comment_ids for a specific post

    full_url = post_comment_endpoint + post_id #adds post id to the url string

    request = requests.get(url=full_url)
    data = []
    if request.status_code == 200:
        response = request.json()
        data = response['data']
    elif request.status_code == 429:
        print("Rate limit exceeded. Sleeping for 5 sec")
        time.sleep(5)
        data = get_post_comment_ids(post_id)
        
    else:
        print("something went wrong")
        print("Tried to pull comment ids of: {}".format(post_id))
        print(f'status code: {request.status_code}')
        
        #sys.exit()

    return data


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
    string and feeds it as a parameter to the pushshift api. 
    '''
    print("Calling get_comments_data method")

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
        request = requests.get(url=CONST_SEARCH_COMMENT_EP, params=params)

        if request.status_code == 200:
            response = request.json()
            all_comment_data = all_comment_data + response['data']
        elif request.status_code == 429:
            print("Rate limit exceeded. Sleeping for 10 sec")
            time.sleep(10)
            all_comment_data = get_comments_data(post_id, comment_ids)
        
        else:
            print("something went wrong")
            print("Tried to pull comment data from post: {}".format(post_id))
            print(f'Tried to pull comments from indices {returned_comments} to {returned_comments + incoming_comments}')
            print(f'status code: {request.status_code}')
            #sys.exit()
        
        
        returned_comments = returned_comments + incoming_comments #increment our returned comments for the while loop
    return all_comment_data # response['data']

###########################################################################################
# Wrapped get commend ids and get comment data into single wrapper to return comment data
# off of a post id
###########################################################################################
def get_comments(post_id):
    comment_ids = get_post_comment_ids(post_id) #an list of comment ids
    comment_data = get_comments_data(post_id, comment_ids)
    return comment_data


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
    print(f"Getting posts from author: {author}")
    all_post_data = []

    #print(author)
    while True:

        params = {
            "author": author,
            "after": since,
            "before": until,
            "size": 500 #max of 500, but we can boost it with a loop and an update to after alla scrape.py file
        }

        request = requests.get(url=CONST_SEARCH_POST_EP, params=params)
        if request.status_code == 200:
            response = request.json()
            all_post_data = all_post_data + response['data']
            if len(response['data']) < 500:
                break
            else: 
                since = response['data'][-1]['created_utc']  
        elif request.status_code == 429:
            print("Rate limit exceeded. Sleeping for 5 sec")
            time.sleep(5)
            all_post_data = get_user_posts(author, since, until)
        else:
            print("something went wrong")
            print("Tried to pull post activity from user: {}".format(author))
            print(f'status code: {request.status_code}')
    #print(len(all_post_data))
    return all_post_data

#####################################################################################
# Parse the JSON returned for each comment. We do not want all the fields returned in
# the response.
#####################################################################################
def parse_comments(comments_data, post_id, post_id_dict):
    '''
    Parse the JSON returned for each comment into releveant fields.
    '''
    parsed_comments = []
    if post_id in post_id_dict and post_id_dict[post_id] == True: #Check if we've already handled the post that these comments are coming from 
        nothing = "do nothing"
    elif len(comments_data) > 0: #If we haven't handled that post, let's check that there are comments to handle
        for comment in comments_data:
            
            comment_id = comment['id']
            if comment_id in post_id_dict:
                continue
            else:
                parsed_comment = {
                    CONST_ID: key_or_nah(comment, CONST_ID),
                    CONST_AUTHOR: key_or_nah(comment, CONST_AUTHOR),
                    CONST_POST_ID: post_id,
                    CONST_BODY: key_or_nah(comment, CONST_BODY),
                    CONST_SCORE: key_or_nah(comment, CONST_SCORE),
                    CONST_CREATED_UTC: key_or_nah(comment, CONST_CREATED_UTC),
                    CONST_RETRIEVED_ON: key_or_nah(comment, CONST_RETRIEVED_ON),
                    CONST_PARENT_ID: key_or_nah(comment, CONST_PARENT_ID),
                    CONST_STICKIED: key_or_nah(comment, CONST_STICKIED),
                    CONST_SUBREDDIT: key_or_nah(comment, CONST_SUBREDDIT),
                    CONST_PERMALINK: key_or_nah(comment, CONST_PERMALINK)
                }

                parsed_comments.append(parsed_comment)
        
    return parsed_comments

#####################################################################################
# Pass the comment text through the classifier and determine if the comment
# is relevant to the Hong Kong protests or not.
#
# Return the relevant comments.
#####################################################################################
def get_relevant_comments(parsed_comments):
    '''
    pass the comment text through the classifier and determine if the comment is relevant to 
    the Hong Kong protests or not.
    Return the relevant comments.
    '''
    relevant_comments = []
    for comment in parsed_comments:
        if comment[CONST_BODY] is not None:
            isRelevant = predict(comment[CONST_BODY])[0]
            if isRelevant == True:
                relevant_comments.append(comment)

    return relevant_comments

#####################################################################################
# Parse the JSON returned for each post. We do not want all the fields returned in
# the response.
#####################################################################################
def parse_posts(all_posts_data, post_id_dict):
    '''
    Parse the JSON returned for each comment. We do not want all the fields returned in
    the response.
    '''
    parsed_posts = []
    
    if len(all_posts_data) > 0:
        for post_data in all_posts_data:
            post_id = post_data['id']
            if post_id in post_id_dict:
                continue
            else:
                parsed_post = {
                CONST_AUTHOR: key_or_nah(post_data, CONST_AUTHOR),
                CONST_CREATED_UTC: key_or_nah(post_data, CONST_CREATED_UTC),
                CONST_FULL_LINK: key_or_nah(post_data, CONST_FULL_LINK),
                CONST_ID: key_or_nah(post_data, CONST_ID),
                CONST_NUMCOMMENTS: key_or_nah(post_data, CONST_NUMCOMMENTS),
                CONST_NUMCROSSPOSTS: key_or_nah(post_data, CONST_NUMCROSSPOSTS),
                CONST_RETRIEVED_ON: key_or_nah(post_data, CONST_RETRIEVED_ON),
                CONST_SCORE: key_or_nah(post_data, CONST_SCORE),
                CONST_SELFTEXT: key_or_nah(post_data, CONST_SELFTEXT),
                CONST_SUBREDDIT: key_or_nah(post_data, CONST_SUBREDDIT),
                CONST_POSTHINT: key_or_nah(post_data, CONST_POSTHINT),
                CONST_SUBREDDIT_SUBSCRIBERS: key_or_nah(post_data, CONST_SUBREDDIT_SUBSCRIBERS),
                CONST_TITLE: key_or_nah(post_data, CONST_TITLE),
                CONST_UPDATED_UTC: key_or_nah(post_data, CONST_UPDATED_UTC),
                CONST_URL: key_or_nah(post_data, CONST_URL)
                }
                

                parsed_posts.append(parsed_post)
            
    return parsed_posts

#####################################################################################
# Pass the post title and text through the classifier and determine if the comment
# is relevant to the Hong Kong protests or not.
#
# Return the relevant posts.
#####################################################################################
def get_relevant_posts(parsed_posts):
    '''
    pass the post title and text through the classifier and determine if the comment is relevant to 
    the Hong Kong protests or not.
    Return the relevant comments.
    '''
    relevant_posts = []
    for post in parsed_posts:
        post_title = "" if post[CONST_TITLE] is None else post[CONST_TITLE]
        post_text = "" if post[CONST_SELFTEXT] is None else post[CONST_SELFTEXT]
        full_text = post_title + ' ' + post_text
       
        isRelevant = predict(full_text)[0]
        if isRelevant == True:
            relevant_posts.append(post)

    return relevant_posts

def is_post_relevant(post):
    '''
    Takes a post and returns True or False depending on whether it is relevant to the 
    Hong Kong protests.
    '''
    post_title = "" if post[CONST_TITLE] is None else post[CONST_TITLE]
    post_text = "" if post[CONST_SELFTEXT] is None else post[CONST_SELFTEXT]
    full_text = post_title + ' ' + post_text
    isRelevant = True if predict(full_text)[0] == 1 else False
    return isRelevant


def key_or_nah(dictionary, key): #
    '''
    Checks to see if a key exists in a dictionary.
    If it does, return its pair value. If not, return nothing
    '''
    if key in dictionary:
        return dictionary[key]
    else:
        return None

def enqueue_post_ids(post_list, post_ids):
    for post in post_list:
        if post['id'] in post_ids:
            nothing = "do nothing"
        else:
            post_ids[post['id']] = False #add post to the post_ids list. Indicate that the post has not been processed yet
    return post_ids
    