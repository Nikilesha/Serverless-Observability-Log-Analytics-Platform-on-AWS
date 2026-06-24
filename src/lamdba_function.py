import json
import boto3
from urllib.parse import unquote_plus

from parser import parse_logs

s3 = boto3.client("s3")


def read_s3_file(bucket, key):
    """Fetch log file content from S3"""
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return content


def write_to_s3(bucket, key, data):
    """Write JSON output back to S3"""
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json"
    )


def lambda_handler(event, context):

    print("Lambda Triggered")
    print(json.dumps(event))

    try:
        # Step 1: Extract bucket and file key from S3 event
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])

        print(f"Bucket: {bucket}")
        print(f"Key: {key}")

        # Step 2: Read log file from S3
        log_content = read_s3_file(bucket, key)

        print("Log file fetched successfully")

        # Step 3: Parse logs → analytics
        analytics = parse_logs(log_content)

        print("Parsing completed")

        # Step 4: Create output path
        file_name = key.split("/")[-1].replace(".log", "_analytics.json")
        output_key = f"output/{file_name}"

        # Step 5: Write analytics back to S3
        write_to_s3(bucket, output_key, analytics)

        print(f"Analytics saved to: {output_key}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Log processed successfully",
                "output_file": output_key
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }