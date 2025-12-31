import streamlit as st
import time
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import textwrap

# --- CUSTOM MODULES (Keep your existing files) ---
from gemini_helper import generate_student_feedback
from auth import auth_page
from styles import load_styles
from data_cleaner import clean_and_standardize_excel
from model import train_regression_model, predict_student_score
from kmeans_clustering import train_kmeans_clustering, save_clustered_excel

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="StudyTrack AI",
    layout="wide",
    page_icon="📚"
)

# ---------------- SESSION STATE INIT ----------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
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

# ---------------- AUTH CHECK ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ---------------- GLOBAL STYLES ----------------
load_styles()

# ---------------- HOME PAGE (SCI-FI TERMINAL) ----------------
if st.session_state.current_page == "home":
    
    # 1. INJECT CSS TO STYLE THE NATIVE STREAMLIT BUTTON
    st.markdown("""
        <style>
            div.stButton > button {
                background: transparent;
                color: #00ff41;
                font-family: 'Space Mono', monospace;
                font-size: 1rem;
                font-weight: bold;
                padding: 15px 40px;
                border: 1px solid #00ff41;
                cursor: pointer;
                text-transform: uppercase;
                transition: all 0.3s ease;
                width: 100%;
                
                /* --- THE NO-SCROLL FIX --- */
                position: relative;
                display: block;
                margin: 0 auto;
                
                /* Using margin-top instead of top removes the empty space at the bottom */
                margin-top: -180px; 
                z-index: 999;
            }

            div.stButton > button:hover {
                background: #00ff41;
                color: #000;
                box-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
                border-color: #00ff41;
            }
            
            div.stButton > button:focus {
                box-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
                color: #000;
                background: #00ff41;
            }
        </style>
    """, unsafe_allow_html=True)
    components.html(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                :root {
                    --bg-color: #0e1117;
                    --card-bg: #161b22;
                    --accent-color: #00ff41;
                    --secondary-color: #008F11;
                    --border-color: #30363d;
                    --text-color: #c9d1d9;
                }
                
                /* --- CRITICAL FIX FOR NO SCROLLING --- */
                html, body {
                    margin: 0; padding: 0;
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    font-family: 'Space Mono', monospace;
                    
                    /* This completely disables scrollbars inside the component */
                    overflow: hidden; 
                    height: 100%;
                }
                
                /* Double insurance to hide scrollbars */
                ::-webkit-scrollbar {
                    display: none;
                }

                .grid-bg {
                    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                    background-image: linear-gradient(var(--border-color) 1px, transparent 1px), linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
                    background-size: 40px 40px; opacity: 0.1; z-index: -1;
                }
                .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
                
                /* HEADER */
                .header-terminal {
                    border: 1px solid var(--border-color); padding: 20px; margin-bottom: 30px; position: relative; background: rgba(22, 27, 34, 0.8);
                }
                .header-terminal::before {
                    content: "SYSTEM_STATUS: ONLINE"; position: absolute; top: -10px; left: 20px;
                    background: var(--bg-color); padding: 0 10px; font-size: 0.7rem; color: var(--accent-color); border: 1px solid var(--border-color);
                }
                h1 { font-size: 2.5rem; margin: 0; text-transform: uppercase; letter-spacing: -2px; color: #fff; }
                .blink { animation: blinker 1s linear infinite; }
                @keyframes blinker { 50% { opacity: 0; } }
                .subtitle { color: #8b949e; margin-top: 10px; font-size: 0.9rem; }

                /* MODULES */
                .modules-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 40px; }
                .module-card { border: 1px solid var(--border-color); background: var(--card-bg); padding: 20px; position: relative; transition: all 0.2s; }
                .module-card:hover { border-color: var(--accent-color); box-shadow: 0 0 15px rgba(0, 255, 65, 0.1); transform: translateY(-2px); }
                .corner { position: absolute; width: 8px; height: 8px; border: 2px solid var(--accent-color); opacity: 0; transition: opacity 0.2s; }
                .c-tl { top: -1px; left: -1px; border-right: 0; border-bottom: 0; }
                .c-tr { top: -1px; right: -1px; border-left: 0; border-bottom: 0; }
                .c-bl { bottom: -1px; left: -1px; border-right: 0; border-top: 0; }
                .c-br { bottom: -1px; right: -1px; border-left: 0; border-top: 0; }
                .module-card:hover .corner { opacity: 1; }
                .mod-icon { font-size: 1.5rem; color: var(--secondary-color); margin-bottom: 15px; }
                .module-card:hover .mod-icon { color: var(--accent-color); }
                .mod-title { font-weight: bold; text-transform: uppercase; margin-bottom: 8px; font-size: 0.9rem; color: #fff; }
                .mod-desc { font-size: 0.75rem; color: #8b949e; line-height: 1.4; }

                /* PIPELINE */
                .pipeline-section { border-top: 1px dashed var(--border-color); padding-top: 30px; position: relative; padding-bottom: 50px; }
                .section-label { margin-bottom: 20px; text-transform: uppercase; color: var(--accent-color); font-size: 0.75rem; letter-spacing: 2px; }
                .pipeline-container { display: flex; align-items: center; justify-content: space-between; position: relative; padding: 20px 0; flex-wrap: wrap; gap: 15px; }
                .pipeline-line { position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: #30363d; z-index: 0; }
                .pipeline-pulse { position: absolute; top: 50%; left: 0; width: 100px; height: 2px; background: linear-gradient(90deg, transparent, var(--accent-color), transparent); z-index: 1; transform: translateY(-50%); animation: pulseMove 4s linear infinite; }
                @keyframes pulseMove { 0% { left: 0%; } 100% { left: 100%; } }
                .node { position: relative; z-index: 2; background: #0d1117; border: 1px solid var(--border-color); padding: 8px 15px; text-align: center; min-width: 80px; }
                .node:hover { border-color: var(--accent-color); color: var(--accent-color); }
                .node-num { font-size: 0.6rem; color: #555; display: block; margin-bottom: 3px; }
                .node-label { font-size: 0.7rem; font-weight: bold; }
                
                .footer { margin-top: 65px; font-size: 0.7rem; color: #484f58; text-align: center; border-top: 1px solid #21262d; padding-top: 15px; }
            </style>
        </head>
        <body>
            <div class="grid-bg"></div>
            <div class="container">
                <div class="header-terminal">
                    <h1>StudyTrack_AI<span class="blink">_</span></h1>
                    <div class="subtitle">> HABIT ANALYSIS & PERFORMANCE PREDICTION PROJECT</div>
                    <div class="subtitle">> DEVELOPED UNDER INFOSYS SPRINGBOARD </div>
                    <div class="subtitle">> UNDER THE GUIDENCE OF MENTOR ANIL KUMAR </div>
                </div>

                <div class="section-label">// SYSTEM_MODULES</div>
                <div class="modules-grid">
                    <div class="module-card">
                        <div class="corner c-tl"></div><div class="corner c-tr"></div><div class="corner c-bl"></div><div class="corner c-br"></div>
                        <div class="mod-icon"><i class="fa-solid fa-database"></i></div>
                        <div class="mod-title">01. PREPROCESS</div>
                        <div class="mod-desc">Cleaning raw datasets. Handling nulls. Standardizing inputs.</div>
                    </div>
                    <div class="module-card">
                        <div class="corner c-tl"></div><div class="corner c-tr"></div><div class="corner c-bl"></div><div class="corner c-br"></div>
                        <div class="mod-icon"><i class="fa-solid fa-calculator"></i></div>
                        <div class="mod-title">02. REGRESSION</div>
                        <div class="mod-desc">Linear Regression algorithm loaded. Predicting scores.</div>
                    </div>
                    <div class="module-card">
                        <div class="corner c-tl"></div><div class="corner c-tr"></div><div class="corner c-bl"></div><div class="corner c-br"></div>
                        <div class="mod-icon"><i class="fa-solid fa-users"></i></div>
                        <div class="mod-title">03. K-MEANS</div>
                        <div class="mod-desc">Unsupervised clustering. Categorizing performance profiles.</div>
                    </div>
                    <div class="module-card">
                        <div class="corner c-tl"></div><div class="corner c-tr"></div><div class="corner c-bl"></div><div class="corner c-br"></div>
                        <div class="mod-icon"><i class="fa-solid fa-terminal"></i></div>
                        <div class="mod-title">04. DASHBOARD</div>
                        <div class="mod-desc">Interactive data visualization and inference engine.</div>
                    </div>
                </div>

                <div class="pipeline-section">
                    <div class="section-label">// EXECUTION_PIPELINE</div>
                    <div class="pipeline-container">
                        <div class="pipeline-line"></div>
                        <div class="pipeline-pulse"></div>
                        <div class="node"><span class="node-num">STEP 01</span> <span class="node-label">AUTH</span></div>
                        <div class="node"><span class="node-num">STEP 02</span> <span class="node-label">UPLOAD</span></div>
                        <div class="node"><span class="node-num">STEP 03</span> <span class="node-label">PROCESS</span></div>
                        <div class="node"><span class="node-num">STEP 04</span> <span class="node-label">CLUSTER</span></div>
                        <div class="node"><span class="node-num">STEP 05</span> <span class="node-label">PREDICT</span></div>
                    </div>
                </div>

                <div class="footer">
                    RUNNING ON PORT 8501 | DEVELOPED BY ABHISHEK JAIN
                </div>
            </div>
        </body>
        </html>
        """,
        height=850, 
        scrolling=False
    )

    # 3. PLACE THE REAL PYTHON BUTTON
    col1, col2, col3 = st.columns([5, 2, 5])
    with col2:
        if st.button("INITIALIZE DASHBOARD >>"):
            st.session_state.current_page = "app"
            st.rerun()

    st.stop()

# ---------------- APP PAGE (DASHBOARD) ----------------
if st.session_state.current_page == "app":

    # --- INJECT DASHBOARD SPECIFIC CSS (To match the Sci-Fi Home Theme) ---
    st.markdown("""
        <style>
            /* Force dark theme for dashboard components */
            .stApp {
                background-color: #0e1117;
            }
            [data-testid="stSidebar"] {
                background-color: #161b22;
                border-right: 1px solid #30363d;
            }
            .stButton>button {
                background-color: #1f6feb;
                color: white;
                border: none;
            }
            .stButton>button:hover {
                background-color: #388bfd;
            }
            h1, h2, h3 {
                font-family: 'Space Mono', monospace;
            }
        </style>
    """, unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("Navigation ->")
    st.sidebar.markdown("---")

    selected_tab = st.sidebar.radio(
        "Select MODULE :",
        ["Data Analysis", "Visualization", "Marks Prediction", "Bulk Prediction"]
    )

    st.sidebar.markdown("---")
    
    if st.sidebar.button("Home"):
        st.session_state.current_page = "home"
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.auth_tab = "signin"
        st.rerun()

    # ---------------- MAIN DASHBOARD CONTENT ----------------
    st.title("StudyTrack AI Dashboard")
    st.markdown("`STATUS: SYSTEM READY`")
    
    st.info("Workflow: Upload Dataset → Clean → Train → Cluster → Predict")
    

    # ---------------- FILE UPLOAD ----------------
    uploaded_file = st.file_uploader(
        "Upload Student Dataset (CSV/Excel)",
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
        st.warning("⚠️ Awaiting Data Input. Please upload a file to proceed.")
        st.stop()

    # ---------------- LOADER (RUNS ONLY ONCE) ----------------
    if not st.session_state.data_processed:
        progress = st.progress(0)
        status = st.empty()

        steps = [
            "Initializing protocols...",
            "Standardizing data format...",
            "Training Regression Model...",
            "Executing K-Means Clustering...",
            "Finalizing visuals..."
        ]

        for i, step in enumerate(steps):
            status.text(f">  {step}")
            progress.progress(int((i + 1) / len(steps) * 100))
            time.sleep(0.5)

        status.text("> PROCESS COMPLETE ")
        time.sleep(1)
        status.empty()
        progress.empty()
        st.session_state.data_processed = True

    # ---------------- DATA PROCESSING ----------------
    
    clean_df, clean_filename, info = clean_and_standardize_excel(
        uploaded_file,
        output_filename="clean_student_data.xlsx"
    )

    # ---------------- MODEL TRAINING ----------------
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

    # ---------------- TABS IMPLEMENTATION ----------------
    
    if selected_tab == "Data Analysis":
        st.subheader("Data Analysis Module")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Processed Data Preview:**")
            st.dataframe(clustered_df.head(10), use_container_width=True)
        with c2:
            st.write("**Dataset Metrics:**")
            st.json({
                "Total Students": len(clustered_df),
                "Features Detected": info["feature_columns_original"],
                "Model MSE": f"{mse:.2f}",
                "Model R2 Score": f"{r2:.3f}"
            })
        
        with open(clean_filename, "rb") as f:
            st.download_button(
                "📥 Download Cleaned Dataset",
                f,
                clean_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif selected_tab == "Visualization":
        st.subheader("Visualization Module")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Cluster Distribution")
            cluster_counts = clustered_df["Cluster_Number"].value_counts().sort_index()
            fig_bar = px.bar(
                x=cluster_counts.index,
                y=cluster_counts.values,
                labels={"x": "Cluster ID Number", "y": "Number of Students"},
                color_discrete_sequence=['#00ff41'] # Hacker green
            )
            fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.markdown("##### Regression Accuracy")
            reg_df = pd.DataFrame({"Actual Marks": y_test, "Predicted Marks": y_pred})
            fig_scatter = px.scatter(
                reg_df, x="Actual Marks", y="Predicted Marks",
                color_discrete_sequence=['#00f2fe'] # Cyan
            )
            fig_scatter.add_shape(
                type="line", x0=reg_df["Actual Marks"].min(), y0=reg_df["Actual Marks"].min(),
                x1=reg_df["Actual Marks"].max(), y1=reg_df["Actual Marks"].max(),
                line=dict(dash="dash", color="white")
            )
            fig_scatter.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_scatter, use_container_width=True)

    elif selected_tab == "Marks Prediction":
        st.subheader("Prediction & Inference")
        
        with st.container(border=True):
            st.markdown("#### New Student Input")
            c1, c2, c3, c4 = st.columns(4)
            # Added step=1.0 to all inputs to increment by 1
            study = c1.number_input("Study Hours", 0.0, 24.0, 5.0, step=1.0)
            work = c2.number_input("Work Hours", 0.0, 24.0, 2.0, step=1.0)
            play = c3.number_input("Play Hours", 0.0, 24.0, 3.0, step=1.0)
            sleep = c4.number_input("Sleep Hours", 0.0, 24.0, 7.0, step=1.0)

            if st.button("RUN PREDICTION PROTOCOL", type="primary", use_container_width=True):
                # Predict
                marks = min(predict_student_score(model, study, work, play, sleep), 100)
                
                # Cluster
                df_new = pd.DataFrame({
                    "StudyHours": [study], "WorkHours": [work], 
                    "PlayHours": [play], "SleepHour": [sleep], "Marks": [marks]
                })
                cluster = kmeans.predict(scaler.transform(df_new))[0]

                remarks = {
                    0: "Performance: OK (Room for Optimization)",
                    1: "Performance: CRITICAL (Needs Improvement)",
                    2: "Performance: EXCELLENT (Maintain Trajectory)"
                }
                
                st.markdown("---")
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.metric(label="Predicted Score", value=f"{marks:.2f}%")
                with res_col2:
                    st.metric(label="Cluster Classification", value=f"Group {cluster}", delta=remarks[cluster])
                
                # Gemini Feedback
                with st.spinner("Connecting to Gemini AI for analysis..."):
                    feedback = generate_student_feedback(study, work, play, sleep, round(marks, 2), cluster)
                
                st.markdown("### 🤖 AI Mentor Analysis")
                st.info(feedback)
    elif selected_tab == "Bulk Prediction":
        st.subheader("Bulk Prediction Module")
        st.info("Upload a dataset of new students (must contain: StudyHours, WorkHours, PlayHours, SleepHour)")

        bulk_file = st.file_uploader("Upload New Student Data", type=["csv", "xlsx"], key="bulk_upload")

        if bulk_file is not None:
            # Load Data
            try:
                if bulk_file.name.endswith('.csv'):
                    new_data = pd.read_csv(bulk_file)
                else:
                    new_data = pd.read_excel(bulk_file)
                
                # Standardize column names (simple cleaning)
                new_data.columns = [c.strip().replace(" ", "") for c in new_data.columns]
                
                # Check for required features
                required_cols = ["StudyHours", "WorkHours", "PlayHours", "SleepHour"]
                missing_cols = [col for col in required_cols if col not in new_data.columns]

                if missing_cols:
                    st.error(f"⚠️ Missing columns: {', '.join(missing_cols)}")
                    st.stop()

                if st.button("RUN BULK PROCESSING", type="primary"):
                    with st.spinner("Processing batch predictions..."):
                        # 1. Prepare Features
                        X_new = new_data[required_cols]

                        # 2. Predict Marks
                        new_data["Predicted_Marks"] = model.predict(X_new)
                        
                        # Clip marks to 0-100 range
                        new_data["Predicted_Marks"] = new_data["Predicted_Marks"].clip(0, 100).round(2)

                        # 3. Predict Clusters (Need to add Marks to X for scaler consistency if scaler was fitted on Marks too)
                        # NOTE: Our scaler/kmeans was trained on features + marks. 
                        # We use the predicted marks to complete the feature set for clustering.
                        X_for_clustering = X_new.copy()
                        X_for_clustering["Marks"] = new_data["Predicted_Marks"]
                        
                        # Scale and Cluster
                        X_scaled = scaler.transform(X_for_clustering)
                        new_data["Cluster_ID"] = kmeans.predict(X_scaled)

                        # 4. Map Remarks
                        remarks_map = {
                            0: "Needs Improvement",
                            1: "Average / Critical",
                            2: "Excellent"
                        }
                        new_data["Status"] = new_data["Cluster_ID"].map(remarks_map)

                    st.success("Batch Processing Complete")
                    
                    # Display Result
                    st.dataframe(new_data.head(10), use_container_width=True)

                    # Download CSV
                    csv = new_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Predicted Results",
                        data=csv,
                        file_name="bulk_predictions.csv",
                        mime="text/csv",
                    )

            except Exception as e:
                st.error(f"Error processing file: {e}")