import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv('GMAIL_APP_PASSWORD')
email = "wdroberts1608@gmail.com"

print(f"Email: {email}")
print(f"Password found: {'Yes' if password else 'No'}")
print(f"Password length: {len(password) if password else 0}")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("TLS connection established")
    server.login(email, password)
    print("✓ Authentication successful!")
    server.quit()
except Exception as e:
    print(f"✗ Authentication failed: {e}")