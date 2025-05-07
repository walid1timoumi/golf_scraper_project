import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

def send_email(subject, content):
    try:
        message = Mail(
            from_email=os.getenv("FROM_EMAIL"),
            to_emails=os.getenv("TO_EMAIL"),
            subject=subject,
            plain_text_content=content
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"✅ Email sent! Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")