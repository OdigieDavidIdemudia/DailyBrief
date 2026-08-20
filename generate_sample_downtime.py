"""Generate a sample Downtime Incident Report for review."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.downtime_report import build_downtime_docx

sample_data = {
    "downtime_id": "SOC/19082026/003",
    "start_date": "19/08/2026",
    "start_time": "9:00 AM",
    "end_date": "19/08/2026",
    "end_time": "2:30 PM",
    "duration": "5 Hours 30 Minutes",
    "reported_by": "David Odigie",
    "position": "Security Monitoring Analyst",
    "system_affected": "IBM QRadar SIEM",
    "severity": "High",
    "impact_summary": (
        "On 19th August 2026, IBM QRadar SIEM experienced a service disruption affecting the "
        "log ingestion pipeline, resulting in delayed event correlation and an inability to "
        "execute real-time searches. The incident impacted the Security Operations Centre's "
        "ability to monitor and respond to security alerts during the outage window. "
        "No permanent data loss was recorded; however, a temporary delay in log processing "
        "of approximately 2 hours was observed. Full restoration of normal operations was "
        "confirmed at 2:30 PM on 19th August 2026."
    ),
    "detection_and_notification": (
        "The SOC team identified the issue at 9:00 AM when log ingestion counters dropped to zero "
        "across multiple data sources.\n"
        "An alert was raised on the QRadar console indicating pipeline failure.\n"
        "The incident was immediately escalated to the SIEM administration team and the MSSP "
        "vendor (Inspira) for investigation."
    ),
    "root_cause_analysis": (
        "Preliminary investigation revealed that the QRadar Event Collector service crashed "
        "due to a misconfigured log source that submitted malformed syslog packets at a rate "
        "exceeding the collector's processing threshold, causing a service thread deadlock."
    ),
    "mitigation_and_recovery": (
        "The malformed log source was identified and temporarily disabled.\n"
        "The QRadar Event Collector service was restarted across all affected nodes.\n"
        "Log backfill was initiated to recover delayed events from the pipeline buffer.\n"
        "Normal ingestion rates were confirmed restored at 2:30 PM."
    ),
    "preventive_measures": (
        "1. Implement input validation rules on all log sources to reject malformed syslog packets.\n"
        "2. Configure QRadar pipeline health dashboards with automated alerting thresholds.\n"
        "3. Conduct a quarterly review of all active log sources to ensure compliance with "
        "ingestion format standards."
    ),
    "internal_communication": (
        "Notified the Unit Head, Security Monitoring.\n"
        "Notified the ISMS Group Head.\n"
        "Notified the Infrastructure and Network teams."
    ),
    "external_communication": (
        "Escalated to Inspira (MSSP) for remote investigation and remediation support."
    ),
    "resource": "N/A",
}

path = build_downtime_docx(sample_data)
print(f"Sample report generated: {path}")
