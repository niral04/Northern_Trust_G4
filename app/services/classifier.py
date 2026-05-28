def classify(alert_type: str, severity: str, service: str | None = None):
    """Route alerts into incident workflows using team-owned orchestration logic."""

    alert_type = alert_type.upper()
    severity = severity.upper()
    service_name = service or ("core-infrastructure" if alert_type == "INFRA" else "application-service")

    if alert_type == "INFRA":
        if severity in {"CRITICAL", "HIGH"}:
            return {
                "priority": "P1" if severity == "CRITICAL" else "P2",
                "workflow_path": "infra_major_incident",
                "assignee": "Infra On-Call",
                "notification_channel": "Slack + SMS",
                "sla_minutes": 15 if severity == "CRITICAL" else 30,
                "remediation_action": f"Restart or fail over {service_name}; validate host/network health",
            }

        return {
            "priority": "P3",
            "workflow_path": "infra_standard_triage",
            "assignee": "Infrastructure Support",
            "notification_channel": "Slack",
            "sla_minutes": 60,
            "remediation_action": f"Run diagnostics for {service_name}",
        }

    if severity in {"CRITICAL", "HIGH"}:
        return {
            "priority": "P2",
            "workflow_path": "app_high_priority",
            "assignee": "Application On-Call",
            "notification_channel": "Slack + Email",
            "sla_minutes": 45,
            "remediation_action": f"Rollback or scale {service_name}; inspect error budget",
        }

    return {
        "priority": "P3",
        "workflow_path": "app_standard_support",
        "assignee": "Application Support",
        "notification_channel": "Email",
        "sla_minutes": 120,
        "remediation_action": f"Create support ticket and inspect {service_name} logs",
    }
