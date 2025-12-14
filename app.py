import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from data_cleaner import clean_and_standardize_excel
from model import train_regression_model, predict_student_score
from kmeans_clustering import train_kmeans_clustering, save_clustered_excel

def login_page():
    st.markdown(
        """
        <div style="
            background:#1e1e1e;
            padding:30px;
            border-radius:15px;
            max-width:400px;
            margin:auto;
            box-shadow:0 0 20px #7b2cbf55;
        ">
            <h2 style="text-align:center;color:#bb86fc;">🔐 StudyTrack AI Login</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

st.set_page_config(
    page_title="StudyTrack AI",
    layout="wide",
    page_icon="📚"
)

st.markdown(
    """
    <style>

    /* Global dark background */
    body {
        background: #0d0d0d;
        color: #e0e0e0;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Main content container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-radius: 12px;
        background-color: rgba(20, 20, 20, 0.85);
        box-shadow: 0 4px 25px rgba(0,0,0,0.5);
        backdrop-filter: blur(8px);
    }

    /* Title styling */
    h1 {
        text-align: center;
        font-weight: 700 !important;
        font-size: 42px !important;
        color: #9d4efc !important;
        text-shadow: 0 0 10px #9d4efc55;
        padding-bottom: 10px;
    }

    /* Subheaders */
    h2, h3, h4 {
        color: #bb86fc !important;
        font-weight: 600 !important;
        text-shadow: 0 0 6px #bb86fc33;
    }

    /* Tabs container */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        padding: 8px;
        border-radius: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #111;
        padding: 10px 16px;
        margin-right: 8px;
        border-radius: 10px;
        font-weight: 600;
        color: #d0d0d0;
    }

    /* Active tab */
    .stTabs [aria-selected="true"] {
        background-color: #6a1fbf !important;
        color: white !important;
        font-weight: 700;
        border-bottom: 3px solid #bb86fc !important;
        text-shadow: 0 0 6px #bb86fcaa;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #7b2cbf, #560bad);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
        font-weight: 600;
        transition: 0.3s ease;
        box-shadow: 0 0 10px #7b2cbf55;
    }

    /* Hover effect */
    .stButton>button:hover {
        transform: scale(1.06);
        background: linear-gradient(135deg, #9d4edd, #7b2cbf);
        box-shadow: 0 0 14px #9d4edd99;
    }

    /* Metrics cards */
    .stMetric {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 0 10px #7b2cbf55;
        color: #e0e0e0 !important;
    }

    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        border: 1px solid #333;
        color: #e0e0e0 !important;
    }

    table td, table th {
        color: #ddd !important;
        background-color: #111 !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    ::-webkit-scrollbar-thumb {
        background: #7b2cbf;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #9d4edd;
    }

    </style>
    """,
    unsafe_allow_html=True
)
st.title("StudyTrack AI Habbit Recommender")
st.write("Upload a student dataset -> Clean it -> Train models -> Cluster students -> Predict marks for a new student")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is None:
    st.info("Please upload an Excel file to get started.")
    st.stop()

st.subheader("Step 1: Clean & Standardize Data")

clean_df, clean_filename, info = clean_and_standardize_excel(
    uploaded_file,
    output_filename="clean_student_data.xlsx"
)

col_a, col_b = st.columns(2)
with col_a:
    st.success("Data cleaned successfully!")
    st.write("**Detected Marks column (original name):**", info["marks_column_original"])

with col_b:
    st.write("**Detected feature columns (original names):**")
    st.json(info["feature_columns_original"])

st.markdown("Cleaned Data Preview")
st.dataframe(clean_df.head())

with open(clean_filename, "rb") as f:
    st.download_button(
        label="📥 Download Cleaned Excel",
        data=f,
        file_name=clean_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_clean",
    )
st.subheader("Step 2: Train Models")

model, mse, r2, X_test, y_test, y_pred = train_regression_model(clean_df)

clustered_df, scaler, kmeans = train_kmeans_clustering(clean_df)

save_clustered_excel(clustered_df, "student_remarks.xlsx")

metric_col1, metric_col2 = st.columns(2)
with metric_col1:
    st.metric("Mean Squared Error", f"{mse:.2f}")
with metric_col2:
    st.metric("R2 Score", f"{r2:.3f}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Data & Clusters", "Regression Visualization", "Predict New Student"])
with tab1:
    st.markdown("### Clustered Student Data")

    show_cols = [
        "Student_ID", "StudyHours", "WorkHours", "PlayHours",
        "SleepHour", "Marks", "Cluster_Number", "Remark"
    ]
    existing_cols = [c for c in show_cols if c in clustered_df.columns]
    st.dataframe(clustered_df[existing_cols].head(20))

    st.markdown("#### Cluster Distribution")
    cluster_counts = clustered_df["Cluster_Number"].value_counts().sort_index()
    st.bar_chart(cluster_counts)

    st.markdown("#### Study Hours vs Marks")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    scatter = ax2.scatter(
        clustered_df["StudyHours"],
        clustered_df["Marks"],
        c=clustered_df["Cluster_Number"],
        cmap="plasma"
    )
    ax2.set_xlabel("Study Hours")
    ax2.set_ylabel("Marks")
    ax2.set_title("K-Means Clusters: Study Hours vs Marks")
    ax2.grid(True)
    handles, labels = scatter.legend_elements(prop="colors", alpha=0.7)
    ax2.legend(handles, [f"Cluster {i}" for i in range(3)], title="Clusters")
    st.pyplot(fig2)

    # Download clustered remarks file
    with open("student_remarks.xlsx", "rb") as f:
        st.download_button(
            label="📥 Download Clustered Remarks Excel",
            data=f,
            file_name="student_remarks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_clusters",
        )
with tab2:
    st.markdown("### Actual vs Predicted Marks")

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.scatter(y_test, y_pred, alpha=0.7)
    ax1.plot(
        [y_test.min(), y_test.max()],
        [y_test.min(), y_test.max()],
        linestyle="--"
    )
    ax1.set_xlabel("Actual Marks")
    ax1.set_ylabel("Predicted Marks")
    ax1.set_title("Actual vs Predicted Marks (Regression Line)")
    ax1.grid(True)
    st.pyplot(fig1)

    st.markdown("#### Sample of Test Data with Predictions")
    reg_view = pd.DataFrame({
        "Actual Marks": y_test.values,
        "Predicted Marks": y_pred
    }).head(20)
    st.dataframe(reg_view)

with tab3:
    st.markdown("### Predict Marks & Performance for a New Student")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        study_h = st.number_input("Study Hours", min_value=0.0, max_value=24.0, value=3.0, step=0.5)
    with c2:
        work_h = st.number_input("Work Hours", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
    with c3:
        play_h = st.number_input("Play Hours", min_value=0.0, max_value=24.0, value=3.0, step=0.5)
    with c4:
        sleep_h = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, value=8.0, step=0.5)

    if st.button("Predict"):
        predicted_marks = predict_student_score(
            model,
            study_h,
            work_h,
            play_h,
            sleep_h
        )
        if(predicted_marks>100):
            predicted_marks=100
        new_student_df = pd.DataFrame({
            "StudyHours": [study_h],
            "WorkHours": [work_h],
            "PlayHours": [play_h],
            "SleepHour": [sleep_h],
            "Marks": [predicted_marks]
        })

        from sklearn.preprocessing import StandardScaler

        new_scaled = scaler.transform(new_student_df)
        new_cluster = kmeans.predict(new_scaled)[0]

        remarks_map = {
            0: "Ok Performance! Can Improve",
            1: "Bad Performance! Needs to Improve",
            2: "Great Performance! Keep it Up"
        }
        new_remark = remarks_map.get(new_cluster, "No Remark")

        st.success(f"🎯 Predicted Marks: **{predicted_marks:.2f}**")
        st.info(f"Cluster: **{new_cluster}** | Remark: **{new_remark}**")

