from datetime import datetime

def generate_health_score(analytics):

    total_logs = analytics.get("total_logs", 0)
    total_errors = analytics.get("total_errors", 0)
    total_warnings = analytics.get("total_warnings", 0)
    logs_by_service = analytics.get("logs_by_service", {})
    error_percentage = analytics.get("error_percentage", 0.0)

    # Avoid division issues
    if total_logs > 0:
        error_rate = round(total_errors / total_logs, 4)
    else:
        error_rate = 0

    # Health score formula
    health_score = 100 - (total_errors * 5) - (total_warnings * 2)

    health_score = max(0, health_score)

    # Status mapping
    if health_score >= 90:
        status = "Excellent"
    elif health_score >= 75:
        status = "Good"
    elif health_score >= 50:
        status = "Warning"
    else:
        status = "Critical"

    # Final report (NO file writing)
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "health_score": health_score,
        "status": status,
        "error_rate": error_rate,
        "error_percentage": error_percentage,
        "total_logs": total_logs,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "logs_by_service": logs_by_service,
    }

    return report
