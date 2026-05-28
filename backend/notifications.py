import requests
from dotenv import load_dotenv
import os

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# ── SLACK ────────────────────────────────────────────

def send_slack(text, blocks=None):
    payload = {"text": text}
    if blocks:
        payload["blocks"] = blocks
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Slack notification sent")
        else:
            print(f"Slack error: {response.status_code}")
    except Exception as e:
        print(f"Slack error: {e}")

def slack_new_incident(incident):
    emoji = "🔴" if incident.severity == "critical" else "🟠" if incident.severity == "high" else "🟡"
    send_slack(
        text=f"{emoji} NEW INCIDENT: {incident.source}",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} NEW {incident.severity.upper()} INCIDENT"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*ID:*\n{incident.incident_id}"},
                    {"type": "mrkdwn", "text": f"*Type:*\n{incident.alert_type.upper()}"},
                    {"type": "mrkdwn", "text": f"*Source:*\n{incident.source}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{incident.severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Assigned To:*\n{incident.assignee}"},
                    {"type": "mrkdwn", "text": f"*Message:*\n{incident.message}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Acknowledge within {incident.escalation_timeout} minutes or this will escalate!*"
                }
            }
        ]
    )

def slack_escalation(incident, escalated_to):
    send_slack(
        text=f"🔺 ESCALATED: {incident.incident_id}",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔺 INCIDENT ESCALATED"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*ID:*\n{incident.incident_id}"},
                    {"type": "mrkdwn", "text": f"*Escalated To:*\n{escalated_to}"},
                    {"type": "mrkdwn", "text": f"*Source:*\n{incident.source}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{incident.severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Type:*\n{incident.alert_type.upper()}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🚨 *Immediate action required!*"
                }
            }
        ]
    )

def slack_resolved(incident, mttr):
    send_slack(
        text=f"✅ RESOLVED: {incident.incident_id} in {mttr} mins",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ INCIDENT RESOLVED"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*ID:*\n{incident.incident_id}"},
                    {"type": "mrkdwn", "text": f"*Source:*\n{incident.source}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{incident.severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*MTTR:*\n{mttr} minutes"},
                    {"type": "mrkdwn", "text": f"*Resolution:*\n{incident.resolution_notes or 'Resolved'}"}
                ]
            }
        ]
    )

def slack_acknowledged(incident, engineer):
    send_slack(
        text=f"👀 ACKNOWLEDGED: {incident.incident_id} by {engineer}",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "👀 INCIDENT ACKNOWLEDGED"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*ID:*\n{incident.incident_id}"},
                    {"type": "mrkdwn", "text": f"*Acknowledged By:*\n{engineer}"},
                    {"type": "mrkdwn", "text": f"*Source:*\n{incident.source}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{incident.severity.upper()}"}
                ]
            }
        ]
    )

# ── DISPATCH ──────────────────────────────────────────

def notify(incident, event_type, **kwargs):
    if event_type == "new":
        slack_new_incident(incident)
    elif event_type == "escalation":
        slack_escalation(incident, kwargs.get("escalated_to", "Senior Engineer"))
    elif event_type == "resolved":
        slack_resolved(incident, kwargs.get("mttr", 0))
    elif event_type == "acknowledged":
        slack_acknowledged(incident, kwargs.get("engineer", "Engineer"))