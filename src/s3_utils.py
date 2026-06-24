import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# --------------------------------------------------
# Create S3 Client
# --------------------------------------------------

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# --------------------------------------------------
# Upload Local File To S3
# --------------------------------------------------

def upload_file_to_s3(local_file_path, s3_key):
    """
    Upload a local file to S3

    Example:
    upload_file_to_s3(
        "logs/airflow.log",
        "logs/airflow.log"
    )
    """

    try:
        s3_client.upload_file(
            local_file_path,
            AWS_BUCKET_NAME,
            s3_key
        )

        print(f"Uploaded: {local_file_path} -> {s3_key}")
        return True

    except FileNotFoundError:
        print(f"File not found: {local_file_path}")
        return False

    except ClientError as error:
        print(f"S3 Upload Error: {error}")
        return False


# --------------------------------------------------
# Upload Streamlit Uploaded File
# --------------------------------------------------

def upload_streamlit_file(uploaded_file, s3_key):
    """
    Upload a Streamlit uploaded file object directly to S3

    Example:
    upload_streamlit_file(
        uploaded_file,
        f"logs/{uploaded_file.name}"
    )
    """

    try:
        s3_client.upload_fileobj(
            uploaded_file,
            AWS_BUCKET_NAME,
            s3_key
        )

        print(f"Uploaded: {uploaded_file.name} -> {s3_key}")
        return True

    except ClientError as error:
        print(f"S3 Upload Error: {error}")
        return False


# --------------------------------------------------
# List Files In Bucket Folder
# --------------------------------------------------

def list_files(prefix=""):
    """
    List files in bucket

    Example:
    list_files("logs/")
    """

    try:
        response = s3_client.list_objects_v2(
            Bucket=AWS_BUCKET_NAME,
            Prefix=prefix
        )

        files = []

        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]

                if key.endswith("/"):
                    continue

                files.append(key)

        return files

    except ClientError as error:
        print(f"List Error: {error}")
        return []


# --------------------------------------------------
# Download File From S3
# --------------------------------------------------

def download_file_from_s3(s3_key, local_file_path):
    """
    Download a file from S3

    Example:
    download_file_from_s3(
        "reports/report.json",
        "output/report.json"
    )
    """

    try:
        s3_client.download_file(
            AWS_BUCKET_NAME,
            s3_key,
            local_file_path
        )

        print(f"Downloaded: {s3_key}")
        return True

    except ClientError as error:
        print(f"Download Error: {error}")
        return False


# --------------------------------------------------
# Check Bucket Connection
# --------------------------------------------------

def test_s3_connection():
    """
    Verify S3 connection
    """

    try:
        s3_client.head_bucket(
            Bucket=AWS_BUCKET_NAME
        )

        print("S3 Connection Successful")
        return True

    except ClientError as error:
        print(f"S3 Connection Failed: {error}")
        return False


# --------------------------------------------------
# Local Testing
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTesting S3 Connection...\n")

    if test_s3_connection():

        print("\nFiles in Bucket:\n")

        files = list_files()

        for file in files:
            print(file)