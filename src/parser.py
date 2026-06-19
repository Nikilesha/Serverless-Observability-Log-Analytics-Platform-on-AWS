import re


def parse_log_file(file_path):

    parsed_logs = []

    severity_levels = [
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ]

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            service = "unknown"
            timestamp = "Unknown"
            severity = "INFO"
            message = ""

            if "|" in line:

                parts = line.split("|", 1)

                service = parts[0].strip()
                content = parts[1].strip()

            else:

                content = line

            timestamp_match = re.search(
                r"\[(.*?)\]",
                content
            )

            if timestamp_match:

                timestamp = timestamp_match.group(1)

            for level in severity_levels:

                if level in content:

                    severity = level
                    break

            if " - " in content:

                message = content.split(" - ", 1)[1]

            else:

                message = content

            parsed_logs.append(
                {
                    "service": service,
                    "timestamp": timestamp,
                    "severity": severity,
                    "message": message
                }
            )

    return parsed_logs