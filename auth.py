import streamlit as st

def auth_page():
    st.markdown(
        """
        <style>
        /* Page background */
        .stApp {
            background: radial-gradient(circle at top, #1a1a2e, #0f0f1a);
        }

        /* Center wrapper */
        .auth-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 0vh;
        }

        /* Auth card */
        .auth-box {
            background: rgba(30, 30, 45, 0.95);
            padding: 25px 32px;
            border-radius: 20px;
            width: 380px;
            box-shadow: 0 25px 60px rgba(123, 44, 191, 0.35);
        }

        .auth-title {
            text-align: center;
            font-size: 30px;
            font-weight: 800;
            color: #bb86fc;
            margin-bottom: 3px;
        }

        .auth-subtitle {
            text-align: center;
            color: #b0b0b0;
            margin-bottom: 12px;
            font-size: 14px;
        }

        /* Buttons */
        .stButton button {
            border-radius: 12px;
            height: 40px;
            font-weight: 600;
            margin-top: 15px;

        }

        /* Input fields */
        .stTextInput input {
            border-radius: 12px;
            padding: 10px;
        }

        /* Divider line */
        .auth-divider {
            height: 1px;
            background: linear-gradient(to right, transparent, #7b2cbf, transparent);
            margin: 18px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "signin"

    # ---------- WRAPPER ----------
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
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
    # ---------- TOGGLE ----------
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True):
            st.session_state.auth_tab = "signin"
            st.rerun()
    with col2:
        if st.button("Sign Up", use_container_width=True):
            st.session_state.auth_tab = "signup"
            st.rerun()

    st.markdown("<div class='auth-divider'></div>", unsafe_allow_html=True)

    # ---------- SIGN IN ----------
    if st.session_state.auth_tab == "signin":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password")

    # ---------- SIGN UP ----------
    else:
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", use_container_width=True):
            if not new_user or not new_pass:
                st.error("All fields are required")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                st.success("Account created successfully!")
                st.session_state.auth_tab = "signin"
                st.rerun()

    # ---------- END ----------
    st.markdown("</div></div>", unsafe_allow_html=True)