from logging import debug
import sqlite3
from app import Flask, request, render_template, session, redirect, url_for
app = Flask(__name__)

def convertbinary(filename):
    #converts digital data into binary format
    with open (filename, "rb") as file:
        blobdata = file.read()
    return blobdata

#inserting data into database
def insertblob(id, name, picture):
    try:
        conn = sqlite3.connect("donation.db")
        cur = conn.cursor()
        photo = convertbinary(picture)
        cur.execute ("INSERT INTO pfp (id, name, picture) values(?, ?, ?);", [id, name, photo])
        conn.commit()
        print ("saved")
        conn.close()
    except sqlite3.Error as error:
        print ("Failed to insert blob data", error)
    
    finally:
        if conn:
            conn.close()
            print ("connection is closed successfully")

@app.route('/testimage', methods=['GET', 'POST'])
def image():
    # insertblob(123412, "test", "/Users/abhiindukuri/thehelpinghandproject/static/helpinghandmain1.jpeg")
    insertblob(54293, "abhi", "/Users/abhiindukuri/thehelpinghandproject/static/carity2.jpeg")
    return "files inserted"



if __name__ == "__main__":
    app.run(debug = True)