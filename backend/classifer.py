def classify_alert(alert_type, metric, value, message):

    # ── INFRASTRUCTURE ──────────────────────────────
    if alert_type == "infrastructure":

        if metric == "server_status" and value == "DOWN":
            return {
                "severity": "critical",
                "assignee": "John (On-Call Engineer)",
                "notify_channel": "slack",
                "escalation_timeout": 5
            }

        if metric == "cpu_usage":
            cpu = int(value.replace("%", ""))
            if cpu >= 95:
                return {
                    "severity": "critical",
                    "assignee": "John (On-Call Engineer)",
                    "notify_channel": "slack",
                    "escalation_timeout": 5
                }
            elif cpu >= 80:
                return {
                    "severity": "high",
                    "assignee": "John (On-Call Engineer)",
                    "notify_channel": "slack",
                    "escalation_timeout": 10
                }

        if metric == "packet_loss":
            loss = int(value.replace("%", ""))
            if loss >= 80:
                return {
                    "severity": "critical",
                    "assignee": "John (On-Call Engineer)",
                    "notify_channel": "slack",
                    "escalation_timeout": 5
                }

        if metric == "disk_usage":
            disk = int(value.replace("%", ""))
            if disk >= 90:
                return {
                    "severity": "high",
                    "assignee": "John (On-Call Engineer)",
                    "notify_channel": "slack",
                    "escalation_timeout": 10
                }

        return {
            "severity": "high",
            "assignee": "John (On-Call Engineer)",
            "notify_channel": "slack",
            "escalation_timeout": 10
        }

    # ── APPLICATION ─────────────────────────────────
    elif alert_type == "application":

        if metric == "error_rate":
            rate = int(value.replace("%", ""))
            if rate >= 40:
                return {
                    "severity": "high",
                    "assignee": "App Support Team",
                    "notify_channel": "email",
                    "escalation_timeout": 20
                }
            elif rate >= 20:
                return {
                    "severity": "medium",
                    "assignee": "App Support Team",
                    "notify_channel": "email",
                    "escalation_timeout": 30
                }

        if metric == "response_time":
            ms = int(value.replace("ms", ""))
            if ms >= 5000:
                return {
                    "severity": "medium",
                    "assignee": "App Support Team",
                    "notify_channel": "email",
                    "escalation_timeout": 30
                }

        if metric == "job_failure_rate":
            return {
                "severity": "medium",
                "assignee": "App Support Team",
                "notify_channel": "email",
                "escalation_timeout": 30
            }

        return {
            "severity": "low",
            "assignee": "App Support Team",
            "notify_channel": "email",
            "escalation_timeout": 60
        }