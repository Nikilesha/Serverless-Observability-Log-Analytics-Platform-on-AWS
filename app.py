import os
import streamlit as st

from src.s3_utils import upload_file_to_s3,list_files,download_file_from_s3

from src.analyzer import run_analyzer
from src.health_score import generate_health_score

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AWS Log Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📊 AWS Log Analytics Platform")
st.markdown(
    "Upload Airflow and PostgreSQL logs, analyze them, "
    "generate health reports, and store everything in Amazon S3."
)

st.divider()

# --------------------------------------------------
# Upload Section
# --------------------------------------------------

st.subheader("Upload Log Files")

airflow_file = st.file_uploader(
    "Upload Airflow Log",
    type=["log", "txt"],
    key="airflow"
)

postgres_file = st.file_uploader(
    "Upload PostgreSQL Log",
    type=["log", "txt"],
    key="postgres"
)

# --------------------------------------------------
# Run Analysis Button
# --------------------------------------------------

if airflow_file and postgres_file:

    st.success("Both log files selected.")

    if st.button("🚀 Run Analysis"):

        try:

            # --------------------------------------------------
            # Create Local Folders
            # --------------------------------------------------

            os.makedirs("logs", exist_ok=True)
            os.makedirs("output", exist_ok=True)

            airflow_path = "logs/airflow.log"
            postgres_path = "logs/postgres.log"

            # --------------------------------------------------
            # Save Uploaded Files Locally
            # --------------------------------------------------

            with open(airflow_path, "wb") as file:
                file.write(airflow_file.getbuffer())

            with open(postgres_path, "wb") as file:
                file.write(postgres_file.getbuffer())

            st.info("Log files saved locally.")

            # --------------------------------------------------
            # Upload Logs To S3
            # --------------------------------------------------

            upload_file_to_s3(
                airflow_path,
                "logs/airflow.log"
            )

            upload_file_to_s3(
                postgres_path,
                "logs/postgres.log"
            )

            st.success("Logs uploaded to S3.")

            # --------------------------------------------------
            # Run Analytics
            # --------------------------------------------------

            run_analyzer(
                airflow_path,
                postgres_path
            )

            st.success("Analytics generated.")

            # --------------------------------------------------
            # Generate Health Report
            # --------------------------------------------------

            report = generate_health_score()

            st.success("Health report generated.")

            # --------------------------------------------------
            # Upload Reports To S3
            # --------------------------------------------------

            upload_file_to_s3(
                "output/analytics.json",
                "reports/analytics.json"
            )

            upload_file_to_s3(
                "output/report.json",
                "reports/report.json"
            )

            st.success("Reports uploaded to S3.")

            st.divider()

            # --------------------------------------------------
            # Dashboard
            # --------------------------------------------------

            st.header("📈 Analytics Dashboard")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Health Score",
                    report["health_score"]
                )

            with col2:
                st.metric(
                    "Status",
                    report["status"]
                )

            col3, col4 = st.columns(2)

            with col3:
                st.metric(
                    "Total Errors",
                    report["total_errors"]
                )

            with col4:
                st.metric(
                    "Total Warnings",
                    report["total_warnings"]
                )

            st.metric(
                "Total Logs",
                report["total_logs"]
            )

            # --------------------------------------------------
            # Service Breakdown
            # --------------------------------------------------

            st.subheader("Service Breakdown")

            st.json(
                report["logs_by_service"]
            )

            # --------------------------------------------------
            # Report JSON
            # --------------------------------------------------

            st.subheader("Generated Report")

            st.json(report)

            # --------------------------------------------------
            # Cloud Storage
            # --------------------------------------------------

            st.divider()

            st.header("☁️ Cloud Storage")

            # List log files

            st.subheader("Stored Logs")

            log_files = list_files("logs/")

            if log_files:

                print(log_files)

                for log_file in log_files:

                    local_file = os.path.join(
                        "logs",
                        os.path.basename(log_file)
                    )

                    download_file_from_s3(
                        log_file,
                        local_file
                    )

                    with open(local_file, "rb") as file:

                        st.download_button(
                            label=f"Download {os.path.basename(log_file)}",
                            data=file,
                            file_name=os.path.basename(log_file)
                        )

            else:

                st.info("No log files found in S3.")

            # List report files

            st.subheader("Stored Reports")

            report_files = list_files("reports/")

            if report_files:

                for report_file in report_files:

                    local_file = os.path.join(
                        "output",
                        os.path.basename(report_file)
                    )

                    download_file_from_s3(
                        report_file,
                        local_file
                    )

                    with open(local_file, "rb") as file:

                        st.download_button(
                            label=f"Download {os.path.basename(report_file)}",
                            data=file,
                            file_name=os.path.basename(report_file)
                        )

            else:

                st.info("No reports found in S3.")

        except Exception as error:

            st.error(
                f"Analysis failed: {str(error)}"
            )

else:

    st.info(
        "Please upload both Airflow and PostgreSQL logs."
    )