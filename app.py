from config import BASE_URL

# Later in your send_verification_email function:
link = f"{BASE_URL}/verify?token={token}"