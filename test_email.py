import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

smtp_host = os.getenv('SMTP_HOST')
smtp_port = int(os.getenv('SMTP_PORT'))
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')
from_email = os.getenv('FROM_EMAIL')

msg = EmailMessage()
msg['Subject'] = 'Test Email'
msg['From'] = from_email
msg['To'] = 'umangxrsharma@gmail.com'
msg.set_content('This is a test email')

try:
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    
    print('Email send successfully')

except Exception as e:
    print('SMTP failed')
    print(repr(e))