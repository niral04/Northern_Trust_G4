def classify(alert_type: str, severity: str):

    if alert_type == "INFRA":
        priority = "P1"
        workflow = "infra_critical"

    else:
        priority = "P3"
        workflow = "app_standard"

    return priority, workflow