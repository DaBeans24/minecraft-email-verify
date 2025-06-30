# app.py

from flask import Flask, request, render_template
import mysql.connector
import smtplib
import uuid
from email.message import EmailMessage
from config import DATABASE_CONFIG, EMAIL_CONFIG

app = Flask(__name__)

# Connect to your Apex-hosted MySQL database
def get_db():
    return mysql.connector.connect(**DATABASE_CONFIG)

# Email sender using Gmail SMTP
def send_verification_email(email, token):
    link = f"http://localhost:5000/verify?token={token}"  # Replace with your real domain

    msg = EmailMessage()
    msg["Subject"] = "Verify Your Minecraft Account"
    msg["From"] = EMAIL_CONFIG["email"]
    msg["To"] = email
    msg.set_content(f"Hi there!\n\nClick this link to verify your account:\n{link}\n\nThanks!")

    with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
        server.starttls()
        server.login(EMAIL_CONFIG["email"], EMAIL_CONFIG["password"])
        server.send_message(msg)

# This sends emails to all pending users
@app.route("/send_all_pending")
def send_pending():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT uuid, email FROM players WHERE status = 'pending'")
    results = cursor.fetchall()

    for uuid_val, email in results:
        token = str(uuid.uuid4())
        cursor.execute("UPDATE players SET token = %s WHERE uuid = %s", (token, uuid_val))
        send_verification_email(email, token)

    db.commit()
    return "✅ Emails sent to all pending users!"

# This route verifies users when they click the email link
@app.route("/verify")
def verify():
    token = request.args.get("token")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT uuid FROM players WHERE token = %s", (token,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE players SET status = 'approved' WHERE token = %s", (token,))
        db.commit()
        return render_template("success.html")
    else:
        return "❌ Invalid or expired verification token."

if __name__ == "__main__":
    app.run(debug=True)

