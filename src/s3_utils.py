import os
import boto3
from botocore.exceptions import ClientError

# --------------------------------------------------
# AWS Config (ONLY for LOCAL / STREAMLIT USE)
# Lambda will IGNORE this and use IAM role instead
# --------------------------------------------------

def get_s3_client():
    """
    Creates S3 client safely for local + cloud compatibility.
    In Lambda, AWS credentials are auto-handled.
    """

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")

    # If running in Lambda, these env vars are NOT required
    if aws_access_key_id and aws_secret_access_key:
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

    # Lambda / IAM Role mode
    return boto3.client("s3", region_name=aws_region)


s3_client = get_s3_client()

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


# --------------------------------------------------
# Upload Local File To S3
# --------------------------------------------------

def upload_file_to_s3(local_file_path, s3_key):
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
# Upload Streamlit File Object
# --------------------------------------------------

def upload_streamlit_file(uploaded_file, s3_key):
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
# List Files in Bucket
# --------------------------------------------------

def list_files(prefix=""):
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
# Test S3 Connection (LOCAL ONLY)
# --------------------------------------------------

def test_s3_connection():
    try:
        s3_client.head_bucket(Bucket=AWS_BUCKET_NAME)
        print("S3 Connection Successful")
        return True

    except ClientError as error:
        print(f"S3 Connection Failed: {error}")
        return False