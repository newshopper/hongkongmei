import psycopg2


#connect to database
conn = psycopg2.connect("dbname=hongkongmei user=postgres password=[insert postgres password here]")

#Create a cursor to perform db actions
cur = conn.cursor()

##########################################
# Resets database to rebuild
###########################################
cur.execute("DROP SCHEMA public CASCADE;")
cur.execute("CREATE SCHEMA public;")
cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
cur.execute("GRANT ALL ON SCHEMA public TO public;")
###########################################



#example commands

#create a table with 3 columns, id which increments with each entr, num which takes an integer and data which takes a string 
cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

#Insert a row into the table. %s denotes an entry to be added. This santizes the inputs to prevent sql injections
cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))


#make changes persistent
conn.commit()

#close communication with the database
cur.close()
conn.close()


print("hello")