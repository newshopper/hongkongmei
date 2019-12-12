import psycopg2 #python library for interacting with postgres databases


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
            created_utc numeric, score int, self_text text, url text, full_link text, num_crossposts smallint, 
            num_comments int, post_hint text, retrieived_utc numeric, updated_utc numeric, subreddit varchar(64), subreddit_subscribers bigint);""") #establishes table for posts. NOTE: needs foreign key execute on author
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
        cur.execute("""CREATE TABLE users (author varchar(64) PRIMARY KEY, joined_utc numeric)""") #establishes table for users
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





# These functions are designed to check whether a post, user or comment has already been stored by our pipeline
# As the network expands, We only want to store information (i.e. posts, users) that we haven't stored yet
# We can do that by maintaining local dictionaries (declared in seed.py) with keys representing the unique id
# of each object
#
# If the new item coming it is new, we add it to our dictionary and store it in our relational database. If not, 
# we ignore it and move on. We use psycopg2 library to interact with our postgres database. In each function you see
# a db_cursor variable passed. 



def store_user(db_cursor, user_dict):  
    print("store user")



def store_post(db_cursor, post_dict):
    print("store post")


def store_comment(db_cursor, comment_dict):
    print("store_comment")