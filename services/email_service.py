
import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer


# 1. Generate password reset token
def generate_reset_token(email):
    """
    Create a unique, time-limited token for password reset.
    The token is tied to the farmer's email and expires after 1 hour.
    """

    secret_key = os.getenv('SECRET_KEY')

    if not secret_key:
        raise ValueError("SECRET_KEY is not configured")

    serializer = URLSafeTimedSerializer(secret_key)

    return serializer.dumps(
        email,
        salt='password-reset-salt'
    )


# 2. Verify password reset token
def verify_reset_token(token, expiration=3600):
    """
    Check if a reset token is valid and not expired.
    Returns the email if valid, otherwise None.
    Default expiration is 1 hour (3600 seconds).
    """

    secret_key = os.getenv('SECRET_KEY')

    if not secret_key:
        raise ValueError("SECRET_KEY is not configured")

    serializer = URLSafeTimedSerializer(secret_key)

    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )

        return email

    except Exception:
        return None


# 3. Send password reset email
def send_reset_email(farmer_email, farmer_name, reset_url):
    """
    Send a password reset email to the farmer.
    """

    sender_email = os.getenv('EMAIL_ADDRESS')
    sender_password = os.getenv('EMAIL_PASSWORD')

    smtp_server = os.getenv(
        'SMTP_SERVER',
        'smtp.gmail.com'
    )

    smtp_port = int(os.getenv('SMTP_PORT', 587))

    # Check email configuration
    if not sender_email or not sender_password:
        print("Email configuration is missing in .env")
        return False

    # Build email message
    message = MIMEMultipart('alternative')

    message['Subject'] = (
        'Reset Your Password - Crop Disease Detection'
    )

    message['From'] = sender_email
    message['To'] = farmer_email

    # Plain text version
    text = f"""Hi {farmer_name},

You asked to reset your password.
Click the link below to set a new one:

{reset_url}

This link expires in 1 hour.

If you didn't ask for this, ignore this email.

Best,
Crop Disease Detection Team
"""

    # HTML version
    html = f"""<html>
    <body>
        <h3>Hi {farmer_name},</h3>

        <p>You asked to reset your password.
        Click the button below to set a new one:</p>

        <p>
            <a href="{reset_url}"
            style="background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            display: inline-block;">
                Reset Password
            </a>
        </p>

        <p>This link expires in 1 hour.</p>

        <p>If you didn't ask for this, ignore this email.</p>

        <p>Best,<br>
        Crop Disease Detection Team</p>
    </body>
    </html>
    """

    # Attach plain text and HTML versions
    message.attach(
        MIMEText(text, 'plain')
    )

    message.attach(
        MIMEText(html, 'html')
    )

    # Send email using SMTP
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.sendmail(
                sender_email,
                farmer_email,
                message.as_string()
            )

        print("Password reset email sent successfully!")

        return True

    except Exception as e:
        print(f"Error sending email: {e}")

        return False
