import boto3
import os

sns = boto3.client("sns")

TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")


def send_alert(service, errors, health_score):
    """
    Send SNS email alert when critical errors are detected.
    """
    print("SNS FUNCTION CALLED")

    message = f"""
Critical Errors Detected

Service: {service}

Errors: {errors}

Health Score: {health_score}
"""

    response = sns.publish(
        TopicArn=TOPIC_ARN, Subject="Critical Log Alert", Message=message
    )

    return response
