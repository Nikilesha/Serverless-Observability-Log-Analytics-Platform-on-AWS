import re


def parse_logs(log_content):

    parsed_logs = []

    severity_levels = [
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ]

    # Split S3 file content into lines
    for line in log_content.splitlines():

        line = line.strip()

        if not line:
            continue

        service = "unknown"
        timestamp = "Unknown"
        severity = "INFO"
        message = ""

        # Example format: service|[timestamp] INFO - message
        if "|" in line:
            parts = line.split("|", 1)
            service = parts[0].strip()
            content = parts[1].strip()
        else:
            content = line

        # Extract timestamp [xxx]
        timestamp_match = re.search(r"\[(.*?)\]", content)

        if timestamp_match:
            timestamp = timestamp_match.group(1)

        # Detect severity
        for level in severity_levels:
            if level in content:
                severity = level
                break

        # Extract message after " - "
        if " - " in content:
            message = content.split(" - ", 1)[1]
        else:
            message = content

        parsed_logs.append({
            "service": service,
            "timestamp": timestamp,
            "severity": severity,
            "message": message
        })

    return parsed_logs