import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

from db import get_connection

def generate_otp():
    return str(random.randint(100000, 999999))

def otp_expiry(minutes=5):
    return datetime.now() + timedelta(minutes=minutes)

def store_otp(email, otp, expiry):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO email_otp (email, otp, expires_at) VALUES (%s, %s, %s)",
        (email, otp, expiry)
    )
    conn.commit()
    cursor.close()
    conn.close()

def verify_otp(email, entered_otp):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM email_otp WHERE email=%s ORDER BY id DESC LIMIT 1",
        (email,)
    )
    record = cursor.fetchone()
    cursor.close()
    conn.close()

    if not record:
        return False

    if record["otp"] != entered_otp:
        return False

    if datetime.now() > record["expires_at"]:
        return False

    return True

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg.set_content(
        f"Your StudyTrack AI verification OTP is: {otp}\n\n"
        "This OTP is valid for 5 minutes."
    )
    msg["Subject"] = "StudyTrack AI – Email Verification"
    msg["From"] = "abhishekjain00e@gmail.com"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("abhishekjain00e@gmail.com", "dsbv tnia hbdk wdsk")
        server.send_message(msg)