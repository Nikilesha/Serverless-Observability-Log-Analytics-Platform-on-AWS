import json
import boto3
from urllib.parse import unquote_plus

from alerts import send_alert
from analyzer import run_analyzer
from parser import parse_logs

s3 = boto3.client("s3")


def read_s3_file(bucket, key):
    """
    Read file from S3
    """
    response = s3.get_object(Bucket=bucket, Key=key)

    return response["Body"].read().decode("utf-8")


def write_to_s3(bucket, key, data):
    """
    Save analytics JSON to S3
    """
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )


def lambda_handler(event, context):

    print("Lambda Triggered")

    try:

        # -----------------------------------
        # Extract S3 details
        # -----------------------------------
        bucket = event["Records"][0]["s3"]["bucket"]["name"]

        key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])

        # -----------------------------------
        # Process ONLY files in logs/
        # -----------------------------------
        if not key.startswith("logs/"):

            print("File not inside logs/ folder. Skipping.")

            return {"statusCode": 200, "body": "Skipped non-log folder file"}

        # -----------------------------------
        # Process ONLY .log files
        # -----------------------------------
        if not key.endswith(".log"):

            print("Not a .log file. Skipping.")

            return {"statusCode": 200, "body": "Skipped non-log file"}

        # -----------------------------------
        # Read log file
        # -----------------------------------
        log_content = read_s3_file(bucket, key)

        print("Log file fetched successfully")

        # -----------------------------------
        # Parse logs
        # -----------------------------------
        parsed_logs = parse_logs(log_content)

        print(f"Parsed {len(parsed_logs)} log records")

        # -----------------------------------
        # Analyze logs
        # -----------------------------------
        analytics = run_analyzer(parsed_logs)

        print("Analysis completed")
        print(json.dumps(analytics, indent=2))

        # -----------------------------------
        # Extract service safely
        # -----------------------------------
        service = "unknown"

        if isinstance(parsed_logs, list) and len(parsed_logs) > 0:
            service = parsed_logs[0].get("service", "unknown")

        # -----------------------------------
        # SNS Alerts
        # -----------------------------------
        try:

            total_errors = analytics.get("total_errors", 0)

            print(f"Total Errors: {total_errors}")

            if total_errors > 0:

                send_alert(
                    service=service,
                    errors=total_errors,
                    health_score=analytics.get("health_score", 0),
                )

                print("SNS alert sent successfully")

            else:

                print("No errors found. Alert skipped.")

        except Exception as sns_error:

            print("SNS Error:", str(sns_error))

        # -----------------------------------
        # Generate output file name
        # -----------------------------------
        file_name = key.split("/")[-1].replace(".log", "_analytics.json")

        output_key = f"output/{file_name}"

        # -----------------------------------
        # Save analytics to S3
        # -----------------------------------
        write_to_s3(bucket, output_key, analytics)

        print(f"Analytics saved to: {output_key}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Log processed successfully", "output_file": output_key}
            ),
        }

    except Exception as e:

        print("Error occurred:", str(e))

        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
