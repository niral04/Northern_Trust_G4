import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EMAIL_SENDER      = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD    = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER    = os.getenv("EMAIL_RECEIVER")

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
                "text": {"type": "plain_text", "text": "🔺 INCIDENT ESCALATED"}
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
                "text": {"type": "mrkdwn", "text": "🚨 *Immediate action required!*"}
            }
        ]
    )

def slack_resolved(incident, mttr):
    send_slack(
        text=f"✅ RESOLVED: {incident.incident_id} in {mttr} mins",
        blocks=[
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ INCIDENT RESOLVED"}
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
                "text": {"type": "plain_text", "text": "👀 INCIDENT ACKNOWLEDGED"}
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

# ── EMAIL ─────────────────────────────────────────────

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From']    = EMAIL_SENDER
        msg['To']      = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def email_new_incident(incident):
    severity_color = {
        "high":   "#f97316",
        "medium": "#eab308",
        "low":    "#22c55e"
    }.get(incident.severity, "#f97316")

    subject = f"[{incident.severity.upper()}] New Incident — {incident.source}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2 style="color: {severity_color}; border-bottom: 2px solid {severity_color}; padding-bottom: 8px;">
            🔔 New Application Incident
        </h2>
        <table border="1" cellpadding="10" cellspacing="0"
               style="width:100%; border-collapse:collapse;">
            <tr><td><b>Incident ID</b></td><td>{incident.incident_id}</td></tr>
            <tr><td><b>Source</b></td><td>{incident.source}</td></tr>
            <tr><td><b>Severity</b></td><td style="color:{severity_color}">
                <b>{incident.severity.upper()}</b></td></tr>
            <tr><td><b>Type</b></td><td>{incident.alert_type.upper()}</td></tr>
            <tr><td><b>Message</b></td><td>{incident.message}</td></tr>
            <tr><td><b>Assigned To</b></td><td>{incident.assignee}</td></tr>
        </table>
        <p style="color:#f97316; font-weight:bold;">
            ⚠️ Please acknowledge within {incident.escalation_timeout} minutes
            or this will escalate!
        </p>
        <p style="color:#888; font-size:12px;">
            Log in to the dashboard to acknowledge or resolve this incident.
        </p>
    </div>
    """
    send_email(subject, body)

def email_escalation(incident, escalated_to):
    subject = f"[ESCALATED] Incident {incident.incident_id} — {incident.source}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2 style="color: #ef4444; border-bottom: 2px solid #ef4444; padding-bottom: 8px;">
            🔺 Incident Escalated
        </h2>
        <p>Incident <b>{incident.incident_id}</b> was not acknowledged in time
           and has been escalated to <b>{escalated_to}</b>.</p>
        <table border="1" cellpadding="10" cellspacing="0"
               style="width:100%; border-collapse:collapse;">
            <tr><td><b>Source</b></td><td>{incident.source}</td></tr>
            <tr><td><b>Severity</b></td><td><b>{incident.severity.upper()}</b></td></tr>
            <tr><td><b>Message</b></td><td>{incident.message}</td></tr>
            <tr><td><b>Escalated To</b></td><td>{escalated_to}</td></tr>
        </table>
        <p style="color:#ef4444; font-weight:bold;">🚨 Immediate action required!</p>
    </div>
    """
    send_email(subject, body)

def email_resolved(incident, mttr):
    subject = f"[RESOLVED] Incident {incident.incident_id} — {incident.source}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2 style="color: #22c55e; border-bottom: 2px solid #22c55e; padding-bottom: 8px;">
            ✅ Incident Resolved
        </h2>
        <table border="1" cellpadding="10" cellspacing="0"
               style="width:100%; border-collapse:collapse;">
            <tr><td><b>Incident ID</b></td><td>{incident.incident_id}</td></tr>
            <tr><td><b>Source</b></td><td>{incident.source}</td></tr>
            <tr><td><b>Severity</b></td><td>{incident.severity.upper()}</td></tr>
            <tr><td><b>MTTR</b></td><td>{mttr} minutes</td></tr>
            <tr><td><b>Resolution</b></td>
                <td>{incident.resolution_notes or 'Resolved'}</td></tr>
        </table>
    </div>
    """
    send_email(subject, body)

# ── DISPATCH ──────────────────────────────────────────

def notify(incident, event_type, **kwargs):
    # Infrastructure → Slack
    # Application    → Email
    if incident.notify_channel == "slack":
        if event_type == "new":
            slack_new_incident(incident)
        elif event_type == "escalation":
            slack_escalation(incident, kwargs.get("escalated_to", "Senior Engineer"))
        elif event_type == "resolved":
            slack_resolved(incident, kwargs.get("mttr", 0))
        elif event_type == "acknowledged":
            slack_acknowledged(incident, kwargs.get("engineer", "Engineer"))

    elif incident.notify_channel == "email":
        if event_type == "new":
            email_new_incident(incident)
        elif event_type == "escalation":
            email_escalation(incident, kwargs.get("escalated_to", "Team Lead"))
        elif event_type == "resolved":
            email_resolved(incident, kwargs.get("mttr", 0))