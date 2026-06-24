import json
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# Paths
# --------------------------------------------------
def generate_health_score():
    BASE_DIR = Path(__file__).resolve().parent.parent

    ANALYTICS_FILE = BASE_DIR / "output" / "analytics.json"
    REPORT_FILE = BASE_DIR / "output" / "report.json"

    # --------------------------------------------------
    # Load analytics data
    # --------------------------------------------------

    try:
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as file:
            analytics = json.load(file)

    except FileNotFoundError:
        raise Exception(f"Analytics file not found: {ANALYTICS_FILE}")
        

    # --------------------------------------------------
    # Extract metrics
    # --------------------------------------------------

    total_logs = analytics.get("total_logs", 0)
    total_errors = analytics.get("total_errors", 0)
    total_warnings = analytics.get("total_warnings", 0)
    logs_by_service = analytics.get("logs_by_service", {})
    error_percentage = analytics.get("error_percentage", 0.0)

    # --------------------------------------------------
    # Calculate error rate
    # --------------------------------------------------

    if total_logs > 0:
        error_rate = round(total_errors / total_logs, 4)
    else:
        error_rate = 0

    # --------------------------------------------------
    # Calculate health score
    # Formula:
    # 100 - errors*5 - warnings*2
    # --------------------------------------------------

    health_score = (
        100
        - (total_errors * 5)
        - (total_warnings * 2)
    )

    # Prevent negative scores

    health_score = max(0, health_score)

    # --------------------------------------------------
    # Determine status
    # --------------------------------------------------

    if health_score >= 90:
        status = "Excellent"

    elif health_score >= 75:
        status = "Good"

    elif health_score >= 50:
        status = "Warning"

    else:
        status = "Critical"

    # --------------------------------------------------
    # Build report
    # --------------------------------------------------

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "health_score": health_score,
        "status": status,
        "error_rate": error_rate,
        "error_percentage": error_percentage,
        "total_logs": total_logs,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "logs_by_service": logs_by_service
    }

    # --------------------------------------------------
    # Save report
    # --------------------------------------------------

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nHealth score report generated successfully!")
    print(f"Health Score : {health_score}")
    print(f"Status       : {status}")
    print(f"Report Saved : {REPORT_FILE}")

    return report

if __name__ == "__main__":
    generate_health_score()