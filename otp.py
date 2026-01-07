import random
import smtplib
import sqlite3
from email.message import EmailMessage
from datetime import datetime, timedelta
import streamlit as st

DB_NAME = "studytrack_ai.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_otp_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_otp (
            email TEXT PRIMARY KEY,
            otp TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generate_otp():
    return str(random.randint(100000, 999999))


def otp_expiry(minutes=5):
    return (datetime.now() + timedelta(minutes=minutes)).isoformat()


def store_otp(email, otp, expiry):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO email_otp (email, otp, expires_at) VALUES (?, ?, ?)",
        (email, otp, expiry)
    )
    conn.commit()
    conn.close()


def verify_otp(email, entered_otp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT otp, expires_at FROM email_otp WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    stored_otp, expires_at = row

    if stored_otp != entered_otp:
        return False

    if datetime.now() > datetime.fromisoformat(expires_at):
        return False

    return True


def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg.set_content(
        f"Your StudyTrack AI verification OTP is: {otp}\n\n"
        "This OTP is valid for 5 minutes."
    )
    msg["Subject"] = "StudyTrack AI – Email Verification"
    msg["From"] = st.secrets["EMAIL_USER"]
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            st.secrets["EMAIL_USER"],
            st.secrets["EMAIL_PASSWORD"]
        )
        server.send_message(msg)