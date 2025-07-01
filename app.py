from flask import Flask, request, render_template
import mysql.connector
import smtplib
import uuid
from email.message import EmailMessage
from config import DATABASE_CONFIG, EMAIL_CONFIG, BASE_URL

app = Flask(__name__)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")  # Show the form

    # POST = form submitted
    print("[DEBUG] /register route hit")
    username = request.form["username"]
    email = request.form["email"]
    token = str(uuid.uuid4())
    print(f"[DEBUG] Received username={username}, email={email}")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO player_registrations (minecraft_username, erau_email, token, status) VALUES (%s, %s, %s, 'PENDING')",
        (username, email, token)
    )
    db.commit()
    print("[DEBUG] Inserted into database")

    try:
        send_verification_email(email, token)
    except Exception as e:
        print(f"[ERROR] Failed to send email during registration: {e}")

    return "✅ Registered and verification email sent!"



# Connect to your Apex hosted MySQL database
def get_db():
    return mysql.connector.connect(**DATABASE_CONFIG)

# Email sender using Gmail SMTP
def send_verification_email(email, token):
    link = f"{BASE_URL}/verify?token={token}"
    print(f"[DEBUG] Sending email to: {email}")
    print(f"[DEBUG] Verification link: {link}")
    
    msg = EmailMessage()
    msg["Subject"] = "Verify Your Minecraft Account"
    msg["From"] = EMAIL_CONFIG["email"]
    msg["To"] = email
    msg.set_content(f"Hi there!\n\nClick this link to verify your account:\n{link}\n\nThanks!")

    try:
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["email"], EMAIL_CONFIG["password"])
            server.send_message(msg)
        print("[DEBUG] Email sent successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

        


# This sends emails to all pending users
@app.route("/send_all_pending")
def send_pending():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT minecraft_username, erau_email FROM player_registrations WHERE status = 'PENDING'")
        results = cursor.fetchall()

        if not results:
            return "ℹ️ No pending users found."

        for username, email in results:
            print(f"📨 Sending to {email} for {username}")
            token = str(uuid.uuid4())
            cursor.execute(
                "UPDATE player_registrations SET token = %s WHERE minecraft_username = %s",
                (token, username)
            )
            send_verification_email(email, token)

        db.commit()
        return "✅ Emails sent to all pending users!"

    except Exception as e:
        return f"❌ Error: {e}"


# This route verifies users when they click the email link
@app.route("/verify")
def verify():
    token = request.args.get("token")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT minecraft_username FROM player_registrations WHERE token = %s", (token,))
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE player_registrations SET status = 'APPROVED' WHERE token = %s",
            (token,)
        )
        db.commit()
        return render_template("success.html")
    else:
        return "❌ Invalid or expired verification token."

# Optional: Test your DB connection on Render
@app.route("/test_db")
def test_db():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        return "✅ Connected to the database!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"

if __name__ == "__main__":
    app.run(debug=True)

