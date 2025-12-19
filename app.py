import streamlit as st
import time
import pandas as pd
import plotly.express as px

from auth import auth_page
from styles import load_styles
from data_cleaner import clean_and_standardize_excel
from model import train_regression_model, predict_student_score
from kmeans_clustering import train_kmeans_clustering, save_clustered_excel

st.set_page_config(
    page_title="StudyTrack AI",
    layout="wide",
    page_icon="📚"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

if not st.session_state.logged_in:
    auth_page()
    st.stop()

load_styles()

st.sidebar.title("Navigation")

selected_tab = st.sidebar.radio(
    "",
    ["Data Analysis", "Visualization", "Marks Prediction"]
)
if st.sidebar.button("Logout", use_container_width=False):
    st.session_state.logged_in = False
    st.session_state.auth_tab = "signin"
    st.rerun()

st.title("StudyTrack AI Habbit Recommender")
st.write(
    "Upload a student dataset -> Clean it -> Train models -> "
    "Cluster students -> Predict marks for a new student"
)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["xlsx", "csv"]
)

if uploaded_file is None:
    st.info("Please upload an Excel or CSV file to get started.")
    st.stop()

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
    time.sleep(2)

status.text("Done!")

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

if selected_tab == "Data Analysis":
    st.markdown("### Clustered Student Data")

    show_cols = [
        "Student_ID", "StudyHours", "WorkHours",
        "PlayHours", "SleepHour", "Marks",
        "Cluster_Number", "Remark"
    ]
    existing_cols = [c for c in show_cols if c in clustered_df.columns]
    st.dataframe(clustered_df[existing_cols].head(20))

    st.markdown("#### Cluster Distribution")
    cluster_counts = clustered_df["Cluster_Number"].value_counts().sort_index()

    fig_bar = px.bar(
        x=cluster_counts.index,
        y=cluster_counts.values,
        labels={"x": "Cluster", "y": "Number of Students"},
        title="Cluster Distribution",
        template="plotly_dark"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### Study Hours vs Marks")
    fig_cluster = px.scatter(
        clustered_df,
        x="StudyHours",
        y="Marks",
        color="Cluster_Number",
        title="K-Means Clusters: Study Hours vs Marks",
        color_continuous_scale="Plasma",
        template="plotly_dark"
    )
    fig_cluster.update_layout(
        xaxis_title="Study Hours",
        yaxis_title="Marks"
    )
    st.plotly_chart(fig_cluster, use_container_width=True)

    with open("student_remarks.xlsx", "rb") as f:
        st.download_button(
            label="📥 Download Clustered Remarks Excel",
            data=f,
            file_name="student_remarks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_clusters",
        )

elif selected_tab == "Visualization":
    st.markdown("### Actual vs Predicted Marks")

    reg_df = pd.DataFrame({
        "Actual Marks": y_test,
        "Predicted Marks": y_pred
    })

    fig_reg = px.scatter(
        reg_df,
        x="Actual Marks",
        y="Predicted Marks",
        title="Actual vs Predicted Marks",
        template="plotly_dark"
    )

    fig_reg.add_shape(
        type="line",
        x0=reg_df["Actual Marks"].min(),
        y0=reg_df["Actual Marks"].min(),
        x1=reg_df["Actual Marks"].max(),
        y1=reg_df["Actual Marks"].max(),
        line=dict(color="cyan", dash="dash")
    )

    st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("#### Sample of Test Data with Predictions")
    st.dataframe(reg_df.head(20))

elif selected_tab == "Marks Prediction":
    st.markdown("### Predict Marks & Performance for a New Student")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        study_h = st.number_input("Study Hours", 0.0, 24.0, 3.0, step=0.5)
    with c2:
        work_h = st.number_input("Work Hours", 0.0, 24.0, 2.0, step=0.5)
    with c3:
        play_h = st.number_input("Play Hours", 0.0, 24.0, 3.0, step=0.5)
    with c4:
        sleep_h = st.number_input("Sleep Hours", 0.0, 24.0, 8.0, step=0.5)

    if st.button("Predict"):
        predicted_marks = predict_student_score(
            model,
            study_h,
            work_h,
            play_h,
            sleep_h
        )

        predicted_marks = min(predicted_marks, 100)

        new_student_df = pd.DataFrame({
            "StudyHours": [study_h],
            "WorkHours": [work_h],
            "PlayHours": [play_h],
            "SleepHour": [sleep_h],
            "Marks": [predicted_marks]
        })

        new_scaled = scaler.transform(new_student_df)
        new_cluster = kmeans.predict(new_scaled)[0]

        remarks_map = {
            0: "Ok Performance! Can Improve",
            1: "Bad Performance! Needs to Improve",
            2: "Great Performance! Keep it Up"
        }

        st.success(f"🎯 Predicted Marks: **{predicted_marks:.2f}**")
        st.info(f"Cluster: **{new_cluster}** | Remark: **{remarks_map[new_cluster]}**")