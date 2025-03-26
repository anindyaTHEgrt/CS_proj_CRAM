import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SMTP_USERNAME': os.getenv('EMAIL_USER'),
    'SMTP_PASSWORD': os.getenv('EMAIL_PASSWORD'),
    'SENDER_EMAIL': os.getenv('EMAIL_USER'),
    'USE_TLS': True
}