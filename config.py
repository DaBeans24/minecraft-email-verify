import os

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}



BASE_URL = os.getenv('BASE_URL')  # e.g., https://minecraft-email-verify.onrender.com
MAILERSEND_API_KEY = os.getenv('MAILERSEND_API_KEY')  # required for sending emails
EMAIL_SENDER = os.getenv('EMAIL_ADDRESS')  # Used in the "from" field for SendGrid
