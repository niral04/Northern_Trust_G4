import requests
import random

alerts = [
    {
        "source": "Prometheus",
        "type": "INFRA",
        "severity": "CRITICAL",
        "message": "Server CPU at 99%"
    },
    {
        "source": "Grafana",
        "type": "APP",
        "severity": "MEDIUM",
        "message": "Login API latency high"
    }
]

payload = random.choice(alerts)

response = requests.post(
    "http://127.0.0.1:8000/alerts/",
    json=payload
)

print(response.json())