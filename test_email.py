from dotenv import load_dotenv
load_dotenv()

from services.email_service import (
    generate_reset_token,
    verify_reset_token,
    send_reset_email
)

# Test email address
email = input("Enter your email address: ")
name = "Test Farmer"

# Generate token
token = generate_reset_token(email)
print("Token generated successfully!")

# Verify token
verified_email = verify_reset_token(token)

if verified_email == email:
    print("Token verification successful!")
else:
    print("Token verification failed!")

# Temporary test link
reset_url = f"http://127.0.0.1:5000/auth/reset/{token}"

# Send test email
result = send_reset_email(email, name, reset_url)

if result:
    print("Email test successful!")
else:
    print("Email sending failed!")