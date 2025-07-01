import time
import requests

while True:
    try:
        r = requests.get("https://minecraft-email-verify.onrender.com/send_all_pending")
        print(f"Pinged /send_all_pending: {r.text}")
    except Exception as e:
        print(f"[ERROR] {e}")
    time.sleep(60)  # Wait 1 minute before next run
