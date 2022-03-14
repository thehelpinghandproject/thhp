from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
from flask_mail import Mail
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
from email.mime.text import MIMEText
app = Flask (__name__)
app.config["SECRET_KEY"] = "1234"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
sender_email = "thehelpinghandprojectorg@gmail.com"
sender_password = "emailverfication!"
mail = Mail(app)

def sendemail(subject, recepient_email, message):
    email_message = MIMEMultipart("alternative")
    email_message["subject"] = subject
    email_message["from"] = sender_email
    email_message["to"] = recepient_email
    part1 = MIMEText(message, "plain")
    email_message.attach(part1)
    context = ssl.create_default_context()
    print(3,context)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password  )
        server.sendmail(
         sender_email, recepient_email, email_message.as_string()
        )

@app.route('/testemail', methods=['GET', 'POST'])
def testemail():
    if request.method == "POST":
        email = request.form.get("email")
        subject = "Welcome"
        message = "Welcome to The Helping Hand Project Website. We are glad to see you join our program. Please confirm this email so that you may be able to do actions towards our program. Thank you!"
        sendemail(subject, email, message)
        print("email sent")

    return render_template ('test2.html')

if __name__ == "__main__":
    app.run(debug=True)
