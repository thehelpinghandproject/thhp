import sqlite3
conn = sqlite3.connect("donation.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE user
(id INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT, lastname TEXT, username TEXT,
city TEXT, state TEXT, zip INTEGER,
email TEXT, password text,
gender TEXT, age INTEGER);""")
print("Table Created")

# cur.execute("CREATE TABLE leaderboard(id rank INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT);")
# print("Table Created")

# cur.execute ("CREATE TABLE userdonation(iddonation INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, donated INTEGER);")
# cur.execute ("DROP TABLE userdonation;")

# cur.execute ("CREATE TABLE pfp (id INTEGER PRIMARY KEY AUTOINCREMENT, picture TEXT);")
# print ("table created")

# cur.execute ("CREATE TABLE verfication (id INTEGER PRIMARY KEY AUTOINCREMENT, status INTEGER DEFAULT 0, user_id INTEGER FORIEGN KEY REFERENCES user(id));") 


conn.commit()
conn.close()