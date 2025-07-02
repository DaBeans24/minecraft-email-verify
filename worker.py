import time
import requests

URL = "https://minecraft-email-verify.onrender.com/send_all_pending"

while True:
    try:
        r = requests.get(URL)
        print(f"Pinged /send_all_pending: {r.text}")
    except Exception as e:
        print(f"[ERROR] {e}")
    time.sleep(60)  # Wait 1 minute before next run
