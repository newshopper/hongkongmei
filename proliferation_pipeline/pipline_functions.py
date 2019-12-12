import requests 
import json
import sys
import random

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
    print("Calling get_post_comment_ids method")
    
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
    print("Calling get_post_data method")
    
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
    
#####################    
# Old code from get_posts_data
######################


    # request = requests.get(url=search_post_endpoint, params=params)

    # if request.status_code == 200:
    #     response = request.json()
    #     data = response['data']
    #     print(data[0])
        # data_dict = {
        #     "author": data['author'],
        #     "created_utc": data['created_utc'],
        #     "full_link": data['full_link'],
        #     "id": data['id'],
        #     "num_comments": data['num_comments'],
        #     "num_crossposts": data['num_crossposts'],
        #     "retrieved_on": data['retrieved_on'],
        #     "score": data['score'],
        #     "selftext": data['selftext'],
        #     "subreddit": data['subreddit'],
        #     "subreddit_subscribers": data['subreddit_subscribers'],
        #     "tite": data['title'],
        #     "updated_utc": data['updated_utc'],
        #     "url": data['url']
        # }
        
        
    # else:
    #     print("something went wrong")
    #     print("Tried to pull post data of: {}".format(post_ids))
    #     print(f'status code: {request.status_code}')
    #     sys.exit() #kill the program

    # return 1 #data_dict

def get_crosspost_ids(url):
    '''
    # Get crosspost ids from the given URL
    # Returns a list of post ids
    '''
    # modify the URL to get the duplicates URL
    dupli_url = url.replace('comments', 'duplicates')
    # add .json to the end of dupli_url
    dupli_url = dupli_url + '.json'
    print(dupli_url)
    # make a GET request for dupli_url and read the JSON data
    request = requests.get(dupli_url)
    
    crosspost_ids = []
    print(request.status_code)
    if request.status_code == 200:
        results = request.json()
        # read the second element of the array
        crossposts_dict = results[1]
        crossposts_array = crossposts_dict['data']['children']
        for crosspost in crossposts_array:
            crosspost_data = crosspost['data']
            crosspost_id = crosspost_data['id']
            crosspost_ids.append(crosspost_id)
    
    return crosspost_ids

def get_crossposts(url):
    crosspost_ids = get_crosspost_ids(url)
    crossposts = get_posts_data(crosspost_ids)
    return crossposts

##################################################################################################

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