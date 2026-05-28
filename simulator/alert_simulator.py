import requests
import time

BACKEND = "http://localhost:8000/api/alerts"

INFRA_ALERTS = [
    {
        "alert_type": "infrastructure",
        "source": "server-01",
        "metric": "server_status",
        "value": "DOWN",
        "message": "Server server-01 completely unresponsive",
        "severity": "critical"
    },
    {
        "alert_type": "infrastructure",
        "source": "network-gateway",
        "metric": "packet_loss",
        "value": "95%",
        "message": "Network gateway packet loss at 95%",
        "severity": "critical"
    },
    {
        "alert_type": "infrastructure",
        "source": "db-server-01",
        "metric": "cpu_usage",
        "value": "99%",
        "message": "Database server CPU at 99% for 10 minutes",
        "severity": "high"
    }
]

APP_ALERTS = [
    {
        "alert_type": "application",
        "source": "payment-service",
        "metric": "error_rate",
        "value": "45%",
        "message": "Payment service error rate spiked to 45%",
        "severity": "high"
    },
    {
        "alert_type": "application",
        "source": "auth-service",
        "metric": "response_time",
        "value": "8500ms",
        "message": "Auth service response time at 8.5 seconds",
        "severity": "medium"
    },
    {
        "alert_type": "application",
        "source": "inventory-service",
        "metric": "job_failure_rate",
        "value": "100%",
        "message": "Inventory sync job failing for 20 minutes",
        "severity": "medium"
    }
]

def fire_alert(alert):
    try:
        res = requests.post(BACKEND, json=alert)
        data = res.json()
        print(f"✅ Created {data['incident_id']} — {data['severity'].upper()} — {alert['source']}")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_demo():
    print("\n🚀 STARTING INCIDENT DEMO\n")
    print("━" * 40)

    print("\n📡 FIRING INFRASTRUCTURE ALERTS...\n")
    fire_alert(INFRA_ALERTS[0])
    time.sleep(2)
    fire_alert(INFRA_ALERTS[1])
    time.sleep(2)

    print("\n📱 FIRING APPLICATION ALERTS...\n")
    fire_alert(APP_ALERTS[0])
    time.sleep(2)
    fire_alert(APP_ALERTS[1])
    time.sleep(2)

    print("\n📡 FIRING MORE ALERTS...\n")
    fire_alert(INFRA_ALERTS[2])
    time.sleep(2)
    fire_alert(APP_ALERTS[2])

    print("\n✅ ALL ALERTS FIRED — Check your dashboard!\n")

if __name__ == "__main__":
    run_demo()