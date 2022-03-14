from passlib.hash import sha256_crypt
from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
from flask_mail import Mail
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
from email.mime.text import MIMEText
import random
app = Flask (__name__)
app.config["SECRET_KEY"] = "1234"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
sender_email = "thehelpinghandprojectorg@gmail.com"
sender_password = "emailverfication!"
mail = Mail(app)

#Sending Email Function
def sendemail(subject, recepient_email, message):
    email_message = MIMEMultipart("alternative")
    email_message["subject"] = subject
    email_message["from"] = sender_email
    email_message["to"] = recepient_email
    part1 = MIMEText(message, "plain")
    email_message.attach(part1)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password  )
        server.sendmail(
         sender_email, recepient_email, email_message.as_string()
        )

#Home Page
@app.route('/')
@app.route('/home')
def home():
    return render_template ("index.html")

#Leaderboard Page
@app.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect("donation.db")
    rank = 1
    cur = conn.cursor()
    cur.execute("SELECT iddonation, user.username, donated, firstname, lastname, row_number() OVER(ORDER BY donated DESC) rownumber FROM user JOIN userdonation ON user.username = userdonation.username;")
    rows = cur.fetchall()
    return render_template ("leaderboard.html", rows = rows, rank = rank)

#Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template ("login.html")
    else:
        username = request.form.get ("username")
        password = request.form.get ("password")
        message = ""
        conn = sqlite3.connect ("donation.db")
        cur = conn.cursor()
        password_db = cur.execute ("SELECT password FROM user where username = ?;", [username]) .fetchone()
        checkpassword = sha256_crypt.verify (password, password_db[0])
        if checkpassword:
            session["username"] = username
            message  = "Login Successful"
            session["logged"] = True
            return render_template ("index.html", message = message)
        else:
            message = "Login NOT Successful"
            return render_template ("login.html", message = message)

#Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template ("signup.html")
    else:
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = request.form.get("zip")
        email = request.form.get("email")
        password = request.form.get("password")
        password = sha256_crypt.encrypt(password)
        confirmpassword = request.form.get("cpassword")
        gender = request.form.get("gender")
        age = 10
        message = ""
        if sha256_crypt.verify(confirmpassword, password):
            conn = sqlite3.connect("donation.db")
            cur = conn.cursor()
            cur.execute ("SELECT email FROM user WHERE email = ?;", [email])
            emailcheck = cur.fetchone()
            cur.execute ("SELECT username FROM user WHERE username = ?;", [username])
            usernamecheck = cur.fetchone()
            if emailcheck != None:
                return render_template ("signup.html", message = "Email already used")
            elif usernamecheck != None:
                return render_template ("signup.html", message = "Username already used")
            session["user"] = True
            cur.execute ("""INSERT INTO user(firstname, lastname, username,
            city, state, zip,
            email, password,
            gender, age) values (?,?,?,?,?,?,?,?,?,?);""",(firstname, lastname, username,city,state,zip,email,password,gender, age))
            conn.commit()
            user_id = cur.execute("SELECT id FROM user WHERE username = ?;", [username]).fetchone()
            user_id = user_id[0]
            status = 0
            session["user_id"] = user_id
            cur.execute ("INSERT INTO verfication (status, user_id) VALUES (?,?);", [status, user_id])
            conn.commit()
            conn.close()
            session["username"] = username
            vcode = random.randrange (1111, 9999)
            session["vcode"] = vcode
            subject = "Registration Verfication Email"
            message = "Hey, You have signed up for The Helping Hand Project's website. Please confirm your email so that we know that you own the account. Your Verfication Code is {}. Thanks, The Helping Hand Project".format(vcode)
            sendemail(subject, email, message)
            return render_template ("verfication.html", message = "Account Created")
        else:
            message = "Passwords do not match"
            return render_template("signup.html", message = "Sign Up Failed")

#Email Verfication Page
@app.route('/verfication', methods = ["GET", "POST"])
def verify():
    if request.method == "GET":
        return render_template ("verfication.html")
    else:
        vcode = session.get ("vcode")
        usergivencode = int(request.form.get('usergivencode'))
        if usergivencode == vcode:
            message = ""
            conn = sqlite3.connect("donation.db")
            cur = conn.cursor()
            cur.execute ("UPDATE verfication SET status = 1 WHERE user_id = ?;", [session.get("user_id")])
            conn.commit()
            conn.close()
            return render_template ("login.html", message = "Verfication Successful")
        else:
            return render_template ("verfication.html")

#Account Page
@app.route('/account', methods=['GET', 'POST'])
def account():
    if session.get("logged"):
        conn = sqlite3.connect("donation.db")
        cur = conn.cursor()
        cur.execute ("SELECT email, city, state, zip, gender, firstname, lastname FROM user WHERE username = ?;", [session.get("username")])
        records = cur.fetchone()
        fullname = records[5] + " " + records[6]
        cur.execute ("SELECT picture FROM pfp WHERE id = 1;")
        picture = cur.fetchone()
        return render_template ("account.html", records = records, fullname = fullname, picture = picture)
    else:
        return render_template ("notlogged.html")

#Forgot Username Page
@app.route('/forgotusername', methods=['GET', 'POST'])
def forgotusername():
    if request.method == "GET":
        return render_template ("forgotusername.html")
    else:
        message = ""
        email = request.form.get ("usergivenemailforgot")
        conn = sqlite3.connect ("donation.db")
        cur = conn.cursor()
        foundusername = cur.execute ("SELECT username, firstname FROM user WHERE email = ?;", [email]).fetchone()
        conn.close()
        if foundusername == None:
            return render_template ("login.html", message = "Email sent with your username")
        else:
            username = foundusername[0]
            name = foundusername[1]
            message = "Hello {}, You have requested to get your username on the website. Your Username is: {}. If this is not your actions, please ignore this message. The Helping Hand Project".format (name, username)
            subject = "Forgot Your Username - The Helping Hand Project"
            vcode = 1234
            sendemail(subject, email, message)
            return render_template ("login.html", message = "Email sent with your username")

#Logout Route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session["logged"] = False
    session.clear()
    return render_template ("index.html")

#Donate Page
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    message = ""
    if request.method == "POST":
        username = session.get("username")
        message = ""
        donationvalue = int(request.form.get("donation"))
        conn = sqlite3.connect("donation.db")
        cur = conn.cursor()
        cur.execute ("SELECT donated FROM userdonation WHERE username=?;", [username])
        records = cur.fetchall()
        if session.get("logged") == True:
            if records == []:
                cur.execute ("""INSERT INTO userdonation(username, donated)
                values (?, ?);""", [username, donationvalue])
            else:
                donatedamount = int(records[0] [0])
                donationvalue += donatedamount
                cur.execute ("UPDATE userdonation SET donated = ? WHERE username=?;", [donationvalue, username])
                conn.commit()
        else:
            return render_template ("donate.html", message = "Login to Donate")
        message = "Donation Successful"
        conn.commit()
        conn.close()
    return render_template ("donate.html", message = message)

#Search on Leaderbaord (username)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form.get("searchbar")
        search = "%" + search + "%"
        conn = sqlite3.connect("donation.db")
        cur = conn.cursor()
        cur.execute ("""SELECT iddonation, user.username, donated, firstname, lastname, row_number() OVER(ORDER BY donated DESC) 
        rownumber FROM user JOIN userdonation ON user.username = userdonation.username WHERE userdonation.username like ?;""", [search])
        searchrecords = cur.fetchall()
        return render_template("leaderboard1.html", searchrecords = searchrecords)

#Edit Profile Page (Profile Picture)
@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    if request.method == "POST":
        picturegiven = request.files["profilepicture"]
        imagepath = "static/media/" + picturegiven.filename
        f = open(imagepath, "wb")
        f.write (picturegiven.read())
        f.close ()
        conn = sqlite3.connect("donation.db")
        cur = conn.cursor()
        cur.execute ("INSERT INTO pfp (picture) VALUES (?);", [imagepath])
        conn.commit()
        conn.close()
        return render_template ("editprofile.html", message = "inserted successfully", records = None)
        
    if session.get("logged"):
        conn = sqlite3.connect("donation.db")
        cur = conn.cursor()
        cur.execute ("SELECT email, city, state, zip, gender, firstname, lastname FROM user WHERE username = ?;", [session.get("username")])
        records = cur.fetchone()
        fullname = records[5] + " " + records[6]
        return render_template ("editprofile.html", records = records, fullname = fullname)
    else:
        return render_template ("notlogged.html")
    


@app.errorhandler(404)
def pagenotfound(e):
    return render_template ("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)


