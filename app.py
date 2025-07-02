from flask import Flask, request, render_template, redirect, url_for
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

    # POST request
    username = request.form["username"]
    email = request.form["email"]
    token = str(uuid.uuid4())

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO player_registrations (minecraft_username, erau_email, token, status) VALUES (%s, %s, %s, 'PENDING')",
        (username, email, token)
    )
    db.commit()

    try:
        send_verification_email(email, token, username)
    except Exception as e:
        print(f"[ERROR] Failed to send email during registration: {e}")

    return redirect(url_for("success_page"))  # ✅ MUST be indented inside the function




# Connect to your Apex hosted MySQL database
def get_db():
    return mysql.connector.connect(**DATABASE_CONFIG)

# Email sender using Gmail SMTP
def send_verification_email(email, token, username):
    link = f"{BASE_URL}/verify?token={token}"
    denied_link = f"{BASE_URL}/deny?token={token}"
    print(f"[DEBUG] Sending email to: {email}")
    print(f"[DEBUG] Verification link: {link}")
    print(f"[DEBUG] Denied link: {denied_link}")

    msg = EmailMessage()
    msg["Subject"] = "Verify Your Minecraft Account"
    msg["From"] = EMAIL_CONFIG["email"]
    msg["To"] = email
    msg.set_content(
        f"""Hello {email},

We received a request to link the Minecraft account '{username}' to this email address ({email}).

Please click the link below to confirm ownership and grant game access:
{link}

Or click here to DENY the request:
{denied_link}

Note: Registration may take up to a few minutes to reflect in-game.

Thank you,  
ERRSA's Minecraft Staff
"""
    )

    try:
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["email"], EMAIL_CONFIG["password"])
            server.send_message(msg)
        print("[DEBUG] Email sent successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

        
@app.route("/test-email")
def test_email():
    test_email = "your-email@example.com"
    test_token = str(uuid.uuid4())
    send_verification_email(test_email, test_token, "TestUser")
    return f"✅ Test email sent to {test_email}!"

@app.route("/", methods=["GET"])
def index():
    return "✅ Server is up!"

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
            send_verification_email(email, token, username)

        db.commit()
        return "✅ Emails sent to all pending users!"

    except Exception as e:
        return f"❌ Error: {e}"

@app.route("/deny")
def deny():
    token = request.args.get("token")

    db = get_db()
    cursor = db.cursor()

    # Check if the token exists
    cursor.execute("SELECT minecraft_username FROM player_registrations WHERE token = %s", (token,))
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE player_registrations SET status = 'DENIED' WHERE token = %s",
            (token,)
        )
        db.commit()
        return """
        <h1>❌ Request Denied</h1>
        <p>This email will not be linked to the Minecraft account.</p>
        <p>If this was a mistake, please re-register or contact the ERRSA Minecraft Staff.</p>
        """
    else:
        return "<h1>⚠️ Invalid or expired token.</h1>"

@app.route("/verify")
def verify():
    token = request.args.get("token")
    print(f"[DEBUG] Received token: {token}")

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
        print(f"[DEBUG] Token verified for user: {result[0]}")
        return render_template("success.html")
    else:
        print("[DEBUG] Invalid or expired token")
        return "❌ Invalid or expired verification token."


@app.route("/success")
def success_page():
    return render_template("success.html")


