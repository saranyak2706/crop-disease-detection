import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")

try:
    print("Connecting to Gmail...")

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=30
    )

    server.set_debuglevel(1)

    print("SMTP connection established!")

    server.ehlo()
    print("EHLO successful!")

    server.starttls()
    print("TLS connection successful!")

    server.ehlo()

    server.login(email, password)
    print("Gmail authentication successful!")

    server.quit()

except Exception as e:
    print("Error type:", type(e).__name__)
    print("Error details:", e)