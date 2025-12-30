import streamlit as st
import time
import pandas as pd
import plotly.express as px

from auth import auth_page
from styles import load_styles
from data_cleaner import clean_and_standardize_excel
from model import train_regression_model, predict_student_score
from kmeans_clustering import train_kmeans_clustering, save_clustered_excel

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
# ---------------- SESSION STATE INIT ----------------
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "model" not in st.session_state:
    st.session_state.model = None
if "scaler" not in st.session_state:
    st.session_state.scaler = None
if "kmeans" not in st.session_state:
    st.session_state.kmeans = None
if "y_test" not in st.session_state:
    st.session_state.y_test = None
if "y_pred" not in st.session_state:
    st.session_state.y_pred = None
if "data_processed" not in st.session_state:
    st.session_state.data_processed = False


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="StudyTrack AI",
    layout="wide",
    page_icon="📚"
)

# ---------------- AUTH ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ---------------- STYLES ----------------
load_styles()

# ---------------- HOME PAGE ----------------
if st.session_state.current_page == "home":

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:60px 20px;
        ">
            <h1 style="font-size:48px;">📚 StudyTrack AI</h1>
            <p style="font-size:20px; max-width:700px; margin:auto; color:#cccccc;">
                An intelligent student habit recommender that analyzes study patterns,
                clusters student performance, and predicts marks using Machine Learning.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="
                background:rgba(255,255,255,0.05);
                padding:30px;
                border-radius:16px;
                text-align:left;
            ">
                <h3>🚀 What this platform does</h3>
                <ul style="line-height:1.8;">
                    <li>📊 Cleans & standardizes student datasets</li>
                    <li>🤖 Trains ML models to predict marks</li>
                    <li>🧠 Clusters students based on habits</li>
                    <li>🎯 Gives performance-based insights</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("➡️ Go to Dashboard", use_container_width=True):
            st.session_state.current_page = "app"
            st.rerun()

    st.stop()
# ---------------- APP PAGE ----------------
if st.session_state.current_page == "app":

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("Navigation")

    selected_tab = st.sidebar.radio(
        "",
        ["Data Analysis", "Visualization", "Marks Prediction"]
    )

    if st.sidebar.button("Home"):
        st.session_state.current_page = "home"
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.auth_tab = "signin"
        st.rerun()

    # ---------------- MAIN ----------------
    st.title("StudyTrack AI Habit Recommender")
    st.write(
        "Upload a student dataset → Clean it → Train models → "
        "Cluster students → Predict marks"
    )

    # ---------------- FILE UPLOAD ----------------
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["xlsx", "csv"]
    )

    # Detect new file upload
    if uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.data_processed = False
        st.session_state.model = None
        st.session_state.scaler = None
        st.session_state.kmeans = None

    uploaded_file = st.session_state.uploaded_file

    if uploaded_file is None:
        st.info("Please upload an Excel or CSV file to get started.")
        st.stop()

    # ---------------- LOADER (RUNS ONLY ONCE) ----------------
    if not st.session_state.data_processed:
        progress = st.progress(0)
        status = st.empty()

        steps = [
            "Loading data...",
            "Cleaning data...",
            "Training model...",
            "Clustering...",
            "Almost done..."
        ]

        for i, step in enumerate(steps):
            status.text(step)
            progress.progress(int((i + 1) / len(steps) * 100))
            time.sleep(1.5)

        status.text("Done ✅")
        st.session_state.data_processed = True

    # ---------------- DATA CLEANING ----------------
    st.subheader("Step 1: Clean & Standardize Data")

    clean_df, clean_filename, info = clean_and_standardize_excel(
        uploaded_file,
        output_filename="clean_student_data.xlsx"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.success("Data cleaned successfully!")
        st.write("**Detected Marks column:**", info["marks_column_original"])

    with col2:
        st.write("**Detected feature columns:**")
        st.json(info["feature_columns_original"])

    st.dataframe(clean_df.head())

    with open(clean_filename, "rb") as f:
        st.download_button(
            "📥 Download Cleaned Excel",
            f,
            clean_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ---------------- MODEL TRAINING ----------------
    st.subheader("Step 2: Train Models")

    if st.session_state.model is None:
        model, mse, r2, X_test, y_test, y_pred = train_regression_model(clean_df)
        clustered_df, scaler, kmeans = train_kmeans_clustering(clean_df)

        st.session_state.model = model
        st.session_state.scaler = scaler
        st.session_state.kmeans = kmeans
        st.session_state.y_test = y_test
        st.session_state.y_pred = y_pred
        st.session_state.mse = mse
        st.session_state.r2 = r2
        st.session_state.clustered_df = clustered_df
    else:
        model = st.session_state.model
        scaler = st.session_state.scaler
        kmeans = st.session_state.kmeans
        y_test = st.session_state.y_test
        y_pred = st.session_state.y_pred
        mse = st.session_state.mse
        r2 = st.session_state.r2
        clustered_df = st.session_state.clustered_df

    save_clustered_excel(clustered_df, "student_remarks.xlsx")

    m1, m2 = st.columns(2)
    m1.metric("Mean Squared Error", f"{mse:.2f}")
    m2.metric("R² Score", f"{r2:.3f}")

    st.markdown("---")
    # ---------------- DATA ANALYSIS TAB ----------------
    if selected_tab == "Data Analysis":
        st.subheader("Clustered Student Data")

        st.dataframe(clustered_df.head(20))

        st.subheader("Cluster Distribution")
        cluster_counts = clustered_df["Cluster_Number"].value_counts().sort_index()

        fig = px.bar(
            x=cluster_counts.index,
            y=cluster_counts.values,
            labels={"x": "Cluster", "y": "Students"},
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- VISUALIZATION TAB ----------------
    elif selected_tab == "Visualization":
        st.subheader("Actual vs Predicted Marks")

        reg_df = pd.DataFrame({
            "Actual": y_test,
            "Predicted": y_pred
        })

        fig = px.scatter(
            reg_df,
            x="Actual",
            y="Predicted",
            template="plotly_dark"
        )

        fig.add_shape(
            type="line",
            x0=reg_df["Actual"].min(),
            y0=reg_df["Actual"].min(),
            x1=reg_df["Actual"].max(),
            y1=reg_df["Actual"].max(),
            line=dict(dash="dash")
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- PREDICTION TAB ----------------
    elif selected_tab == "Marks Prediction":
        st.subheader("Predict Marks for a New Student")

        c1, c2, c3, c4 = st.columns(4)
        study = c1.number_input("Study Hours", 0.0, 24.0, 3.0)
        work = c2.number_input("Work Hours", 0.0, 24.0, 2.0)
        play = c3.number_input("Play Hours", 0.0, 24.0, 3.0)
        sleep = c4.number_input("Sleep Hours", 0.0, 24.0, 8.0)

        if st.button("Predict"):
            marks = min(
                predict_student_score(model, study, work, play, sleep),
                100
            )

            df_new = pd.DataFrame({
                "StudyHours": [study],
                "WorkHours": [work],
                "PlayHours": [play],
                "SleepHour": [sleep],
                "Marks": [marks]
            })

            cluster = kmeans.predict(scaler.transform(df_new))[0]

            remarks = {
                0: "Ok Performance! Can Improve",
                1: "Bad Performance! Needs to Improve",
                2: "Great Performance! Keep it Up"
            }

            st.success(f"🎯 Predicted Marks: **{marks:.2f}**")
            st.info(f"Cluster: **{cluster}** | {remarks[cluster]}")