import psycopg2 #python library for interacting with postgres databases
from psycopg2.extras import execute_values

########################################################################
# To connect to the aws database, you need the proper credentials
# 
# dbname, user, password, host and port are all required
# These variables are set in our main script, seed.py 
#######################################################################



def open_database(dbname, user, password, endpoint, port):
    #connect to database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=endpoint, port=port)
    return conn

#Create a cursor to perform db actions
def set_cursor(conn):
    cur = conn.cursor()
    return cur

def wipe_database(cur):
    ##########################################
    # Resets database to rebuild
    ###########################################
    cur.execute("DROP SCHEMA public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    ###########################################

#Close database at the end
def close_database(conn, cursor):
    cursor.close()
    conn.close()
    
######################################################
# The three functions below create three tables
# One table for posts, one for comments and one for users
#
# Three functions are wrapped in one main function "create_tables"
# which adds foreign key dependancies
######################################################

def create_posts_table(cur,conn):
    try:
        cur.execute("""CREATE TABLE posts (post_id varchar(64) PRIMARY KEY, title text, author varchar(64) references users(author), 
            created_utc numeric, score int, selftext text, url text, full_link text, num_crossposts smallint, 
            num_comments int, post_hint text, retrieved_utc numeric, updated_utc numeric, subreddit varchar(64), subreddit_subscribers bigint);""") #establishes table for posts. NOTE: needs foreign key execute on author
        print("create posts table")
        conn.commit() #make changes persistent
    except:
        print("something went wrong creating the posts table")

def create_comments_table(cur,conn):
    try:
        cur.execute("""CREATE TABLE comments (comment_id varchar(64) PRIMARY KEY, post_id varchar(64) references posts(post_id), 
        author varchar(64) references users(author), body text, score int, created_utc numeric, retrieved_utc numeric, parent_id varchar(64), 
        permalink text, subreddit varchar(64), stickied bool)""") #establishes table for comments. NOTE: needs foreign key for post_id and author
        print("create comments table")
        conn.commit() #make changes persistent
    except:
        print("something went wrong creating the comments table")

def create_users_table(cur,conn):
    try:
        cur.execute("""CREATE TABLE users (author varchar(64) PRIMARY KEY, joined_utc numeric, first_appeared_utc numeric)""") #establishes table for users
        print("create users table")
        conn.commit() #make changes persistent
    except:
        print("something went wrong creating the comments table")

########################################################################################
# create_tables takes a database connection and a database cursor and makes the three
# tables to capture relevant reddit data
########################################################################################
def create_tables(cur,conn):
    create_users_table(cur,conn)
    create_posts_table(cur,conn)
    create_comments_table(cur,conn)

    conn.commit()



##########################################################################################
# Wrap SQL insert functions
###########################################################################################

def db_push(cur, conn, user_dict=None, post_list=None, comment_list=None):
    if user_dict != None: #check if method has users to store
        store_users(cur, conn, user_dict)
    if post_list != None: #check if method has posts to store
        store_posts(cur, conn, post_list) 
    if comment_list != None: #check if method has comments to store
        store_comments(cur, conn, comment_list)



##########################################################################################
# These three functions wrap around SQL insert functions
###########################################################################################

##########################################################################################
# Takes a dictionary of users and inserts them into users table in database
# 
# First, converts dictionary to list of user tuples  
# 
# Data must be arranged in order corresponding to columns listed in the sql query
# e.g. (author, joined_utc, first_appeared_utc)
###########################################################################################

def store_users(cur, conn, user_dict):  
    
    db_user_data = []

    for key in user_dict.keys():
        user_tuple = (key, None, user_dict[key]['first_appeared_utc']) #turn dict into tuple
        db_user_data.append(user_tuple) #add tuple to list of users 
    

    execute_values(cur, 
    """INSERT INTO users (author, joined_utc, first_appeared_utc) VALUES %s
    ON CONFLICT (author) DO NOTHING""", db_user_data)
    conn.commit()

    print("Storing new users")



##########################################################################################
# Inserts a list of post data into posts table in database
#
# First, converts list of post dictionaries into a list of post tuples
# 
# Data must be arranged in order corresponding to columns listed in the sql query
# e.g. (post_id, title, author, created_utc, score, self_text, url, full_link, num_crossposts, 
# num_comments, post_hint, retrieved_utc, updated_utc, subreddit, subreddit_subscribers)
##########################################################################################

def store_posts(cur, conn, post_list):
    
    db_post_data = []

    for post in post_list:
        if "post_hint" not in post:
            post['post_hint'] = None
        post_tuple = (post['id'], post['title'], post['author'], post['created_utc'], post['score'], post['selftext'], post['url'], post['full_link'], post['num_crossposts'], post['num_comments'], post['post_hint'], post['retrieved_on'], post['updated_utc'], post['subreddit'], post['subreddit_subscribers']) #build tuple for each post entry
        db_post_data.append(post_tuple)
   
    execute_values(cur,
    """INSERT INTO posts (post_id, title, author, created_utc, score, 
    selftext, url, full_link, num_crossposts, num_comments, post_hint,
    retrieved_utc, updated_utc, subreddit, subreddit_subscribers) VALUES %s 
    ON CONFLICT (post_id) DO NOTHING""", db_post_data)

    conn.commit()
    
    print("Storing posts")


##########################################################################################
# Inserts a list of comment data into comments table in database
#
# First, converts list of comment dictionaries into a list of comment tuples
# 
# Data must be arranged in order corresponding to columns listed in the sql query
# e.g. (comment_id, post_id, author, body, score, created_utc, 
#    retrieved_utc, parent_id, permalink, subreddit, stickied)
##########################################################################################


def store_comments(cur, conn, comment_list):

    db_comment_data = []

    for comment in comment_list:
        comment['post_id'] = "degek8"
        comment_tuple = (comment['id'], comment['post_id'], comment['author'], comment['body'], comment['score'], comment['created_utc'], comment['retrieved_on'], comment['parent_id'], comment['permalink'], comment['subreddit'], comment['stickied']) #Turn comment into tuple 
        db_comment_data.append(comment_tuple)


    execute_values(cur,
    """INSERT INTO comments (comment_id, post_id, author, body, score, created_utc, 
    retrieved_utc, parent_id, permalink, subreddit, stickied) VALUES %s 
    ON CONFLICT (comment_id) DO NOTHING""", db_comment_data)

    conn.commit()
    
    print("Storing comments")