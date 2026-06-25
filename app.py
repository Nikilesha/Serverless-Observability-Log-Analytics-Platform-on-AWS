import os
import json
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from src.s3_utils import upload_file_to_s3, download_file_from_s3, list_files

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AWS Log Analytics Platform", page_icon="📊", layout="wide"
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📊 AWS Log Analytics Platform")
st.markdown(
    "Upload Airflow and PostgreSQL logs. "
    "Lambda will process them and generate reports in S3."
)


st.divider()

# --------------------------------------------------
# Upload Section
# --------------------------------------------------

st.subheader("Upload Log Files")

airflow_file = st.file_uploader(
    "Upload Airflow Log", type=["log", "txt"], key="airflow"
)

postgres_file = st.file_uploader(
    "Upload PostgreSQL Log", type=["log", "txt"], key="postgres"
)

# --------------------------------------------------
# Helper: Load report from S3
# --------------------------------------------------
def load_report():
    try:
        # download latest report from S3
        success = download_file_from_s3("reports/report.json", "output/report.json")

        if not success:
            return None

        with open("output/report.json", "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return None


# --------------------------------------------------
# Upload & Trigger Lambda
# --------------------------------------------------

if airflow_file and postgres_file:

    st.success("Both log files selected.")

    if st.button("🚀 Upload & Analyze via Lambda"):

        try:
            # ------------------------------
            # Ensure folders exist
            # ------------------------------
            os.makedirs("logs", exist_ok=True)
            os.makedirs("output", exist_ok=True)

            airflow_path = "logs/airflow.log"
            postgres_path = "logs/postgres.log"

            # ------------------------------
            # Save files locally (cache only)
            # ------------------------------
            with open(airflow_path, "wb") as f:
                f.write(airflow_file.getbuffer())

            with open(postgres_path, "wb") as f:
                f.write(postgres_file.getbuffer())

            # ------------------------------
            # Upload to S3 (THIS triggers Lambda)
            # ------------------------------
            upload_file_to_s3(airflow_path, "logs/airflow.log")
            upload_file_to_s3(postgres_path, "logs/postgres.log")

            st.success("Logs uploaded to S3 🚀")
            st.info("Lambda is processing logs... please wait a few seconds")

            # ------------------------------
            # Wait for Lambda to process
            # ------------------------------
            with st.spinner("Waiting for AWS Lambda to process logs..."):
                time.sleep(8)

            # ------------------------------
            # Load final report from S3
            # ------------------------------
            report = load_report()

            if report:

                st.success("Report loaded from S3 ✅")

                st.divider()

                # --------------------------------------------------
                # Dashboard
                # --------------------------------------------------

                st.header("📈 Analytics Dashboard")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Health Score", report["health_score"])

                with col2:
                    st.metric("Status", report["status"])

                col3, col4 = st.columns(2)

                with col3:
                    st.metric("Total Errors", report["total_errors"])

                with col4:
                    st.metric("Total Warnings", report["total_warnings"])

                st.metric("Total Logs", report["total_logs"])

                # --------------------------------------------------
                # Detailed View
                # --------------------------------------------------

                st.subheader("Service Breakdown")
                st.json(report["logs_by_service"])

                st.subheader("Full Report")
                st.json(report)

            else:
                st.warning("Report not ready yet. Please try again in a few seconds.")

        except Exception as error:
            st.error(f"Upload failed: {str(error)}")

else:

    st.info("Please upload both Airflow and PostgreSQL logs.")