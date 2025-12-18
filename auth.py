import streamlit as st
import bcrypt

from db import create_user, get_user
from otp import (
    generate_otp,
    otp_expiry,
    store_otp,
    verify_otp,
    send_otp_email
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def auth_page():

    # ---------- SESSION STATE INIT ----------
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "signin"

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "otp_sent" not in st.session_state:
        st.session_state.otp_sent = False

    if "pending_signup" not in st.session_state:
        st.session_state.pending_signup = {}

    # ---------- STYLES ----------
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #1a1a2e, #0f0f1a);
        }

        .auth-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .auth-box {
            background: rgba(30, 30, 45, 0.95);
            padding: 26px 32px;
            border-radius: 20px;
            width: 380px;
            box-shadow: 0 25px 60px rgba(123, 44, 191, 0.35);
        }

        .auth-title {
            text-align: center;
            font-size: 30px;
            font-weight: 800;
            color: #bb86fc;
        }

        .auth-subtitle {
            text-align: center;
            color: #b0b0b0;
            margin-bottom: 14px;
            font-size: 14px;
        }

        .stButton button {
            border-radius: 12px;
            height: 40px;
            font-weight: 600;
            margin-top: 12px;
        }

        .stTextInput input {
            border-radius: 12px;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    subtitle = (
        "Sign in to continue"
        if st.session_state.auth_tab == "signin"
        else "Create your account"
    )

    st.markdown(
        f"""
        <div class="auth-wrapper">
            <div class="auth-box">
                <div class="auth-title">StudyTrack AI</div>
                <div class="auth-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    _, center, _ = st.columns([1, 1, 1])
    with center:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign In", use_container_width=True):
                st.session_state.auth_tab = "signin"
                st.rerun()
        with c2:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.auth_tab = "signup"
                st.rerun()

    _, center, _ = st.columns([1, 1, 1])

    with center:
        if st.session_state.auth_tab == "signin":
            username = st.text_input("USERNAME")
            password = st.text_input("PASSWORD", type="password")

            if st.button("Login", use_container_width=True):
                user = get_user(username)

                if user and check_password(password, user["password_hash"]):
                    st.session_state.logged_in = True
                    st.session_state.username = user["username"]
                    st.rerun()
                else:
                    st.markdown(
                        "<p style='color:#ff4b4b; text-align:center;'>Invalid username or password</p>",
                        unsafe_allow_html=True
                    )
        else:
            email = st.text_input("EMAIL")
            new_user = st.text_input("USERNAME")
            new_pass = st.text_input("PASSWORD", type="password")
            confirm_pass = st.text_input("CONFIRM PASSWORD", type="password")

            # ----- STEP 1: SEND OTP -----
            if not st.session_state.otp_sent:
                if st.button("Send OTP", use_container_width=True):

                    if not email or not new_user or not new_pass or not confirm_pass:
                        st.error("All fields are required")

                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match")

                    else:
                        otp = generate_otp()
                        expiry = otp_expiry()

                        store_otp(email, otp, expiry)
                        send_otp_email(email, otp)

                        st.session_state.otp_sent = True
                        st.session_state.pending_signup = {
                            "email": email,
                            "username": new_user,
                            "password": new_pass
                        }

                        st.success("OTP sent to your email")
            else:
                entered_otp = st.text_input("ENTER OTP")

                if st.button("Verify OTP & Create Account", use_container_width=True):

                    data = st.session_state.pending_signup
                    email = data["email"]
                    username = data["username"]
                    password = data["password"]

                    if verify_otp(email, entered_otp):
                        hashed = hash_password(password)
                        success = create_user(username, hashed)

                        if success:
                            st.success("Account created successfully!")
                            st.session_state.auth_tab = "signin"
                            st.session_state.otp_sent = False
                            st.session_state.pending_signup = {}
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Invalid or expired OTP")