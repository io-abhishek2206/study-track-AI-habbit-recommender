import streamlit as st

def load_styles():
    st.markdown(
        """
        <style>

        body {
            background: #0d0d0d;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            border-radius: 12px;
            background-color: rgba(20, 20, 20, 0.85);
            box-shadow: 0 4px 25px rgba(0,0,0,0.5);
        }

        h1 {
            font-size: 42px !important;
            color: #9d4efc !important;
        }

        h2, h3, h4 {
            color: #bb86fc !important;
        }

        /* ================= SIDEBAR ================= */

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0f1a, #090909);
            padding-top: 0 !important;
        }

        section[data-testid="stSidebar"] input[type="radio"] {
            display: none;
        }

        section[data-testid="stSidebar"] .stRadio > div {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
            width: 100%;
            height: 52px;
            display: flex;
            align-items: center;
            padding: 0 18px;
            background: #141414;
            border-radius: 14px;
            border: 1px solid #262626;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
        }

        section[data-testid="stSidebar"] 
        .stRadio div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #7b2cbf, #560bad);
            color: white !important;
            box-shadow: 0 0 14px #7b2cbf99;
        }

        footer { visibility: hidden; }

        </style>
        """,
        unsafe_allow_html=True
    )