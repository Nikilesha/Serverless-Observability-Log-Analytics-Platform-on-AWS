from collections import Counter


def run_analyzer(all_logs):

    total_logs = len(all_logs)

    total_info = sum(
        1 for log in all_logs
        if log["severity"] == "INFO"
    )

    total_warnings = sum(
        1 for log in all_logs
        if log["severity"] == "WARNING"
    )

    total_errors = sum(
        1 for log in all_logs
        if log["severity"] == "ERROR"
    )

    total_critical = sum(
        1 for log in all_logs
        if log["severity"] == "CRITICAL"
    )

    error_percentage = 0

    if total_logs > 0:
        error_percentage = round(
            (total_errors / total_logs) * 100,
            2
        )

    service_counter = Counter()
    error_counter = Counter()

    for log in all_logs:

        service_counter[log["service"]] += 1

        if log["severity"] == "ERROR":
            error_counter[log["message"]] += 1

    analytics = {
        "total_logs": total_logs,
        "total_info": total_info,
        "total_warnings": total_warnings,
        "total_errors": total_errors,
        "total_critical": total_critical,
        "error_percentage": error_percentage,
        "logs_by_service": dict(service_counter),
        "top_errors": dict(error_counter.most_common(10))
    }

    return analytics