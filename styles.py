import streamlit as st

def load_styles():
    st.markdown(
        """
        <style>

        /* ================= GLOBAL ================= */

        body {
            background: linear-gradient(135deg, #020617, #020617);
            color: #e5e7eb;
            font-family: 'Segoe UI', sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #020617, #020617);
        }

        .block-container {
            padding: 2rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(14px);
            box-shadow:
                0 20px 50px rgba(0,0,0,0.7),
                inset 0 1px 0 rgba(255,255,255,0.05);
            transform: perspective(1200px) translateZ(0);
        }

        /* ================= HEADINGS ================= */

        h1 {
            font-size: 44px !important;
            color: #60a5fa !important;
            text-shadow: 0 0 18px rgba(96,165,250,0.6);
        }

        h2, h3, h4 {
            color: #93c5fd !important;
            text-shadow: 0 0 10px rgba(147,197,253,0.4);
        }

        /* ================= SIDEBAR ================= */

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617, #020617);
            box-shadow: inset -1px 0 0 rgba(255,255,255,0.06);

        }

        section[data-testid="stSidebar"] input[type="radio"] {
            display: none;
        }

        section[data-testid="stSidebar"] .stRadio > div {
            display: flex;
            flex-direction: column;
            gap: 14px;
            padding: 12px;
        }

        section[data-testid="stSidebar"]
        .stRadio div[role="radiogroup"] > label {
            height: 56px;
            width: 100%;
            display: flex;
            align-items: center;
            padding: 0 18px;
            background: linear-gradient(145deg, #020617, #020617);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            box-shadow:
                0 6px 14px rgba(0,0,0,0.6),
                inset 0 1px 0 rgba(255,255,255,0.06);
        }

        section[data-testid="stSidebar"]
        .stRadio div[role="radiogroup"] > label:hover {
            transform: translateY(-2px);
            box-shadow:
                0 10px 22px rgba(0,0,0,0.75),
                0 0 14px rgba(96,165,250,0.25);
        }

        section[data-testid="stSidebar"]
        .stRadio div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #2563eb, #1e40af);
            color: white !important;
            box-shadow:
                0 12px 26px rgba(37,99,235,0.6),
                0 0 24px rgba(96,165,250,0.6);
            transform: translateY(-2px);
        }

        /* ================= GLASS CARDS ================= */

        .glass-card {
            background: rgba(30, 41, 59, 0.55);
            backdrop-filter: blur(14px);
            border-radius: 20px;
            padding: 26px;
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow:
                0 20px 45px rgba(0,0,0,0.65),
                inset 0 1px 0 rgba(255,255,255,0.08);
            transition: all 0.3s ease;
            transform: perspective(1000px) translateZ(0);
        }

        .glass-card:hover {
            transform: perspective(1000px) translateZ(40px) scale(1.03);
            box-shadow:
                0 30px 60px rgba(0,0,0,0.85),
                0 0 30px rgba(96,165,250,0.35);
        }

        /* ================= TEXT ================= */

        .section-title {
            font-size: 26px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #bfdbfe;
        }

        .subtitle {
            font-size: 16px;
            opacity: 0.85;
            color: #c7d2fe;
        }

        .feature {
            font-size: 15px;
            opacity: 0.9;
            color: #e0e7ff;
        }

        /* ================= CLEANUP ================= */

        footer { visibility: hidden; }

        </style>
        """,
        unsafe_allow_html=True
    )