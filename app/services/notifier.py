import os
import smtplib
import requests

from dotenv import load_dotenv

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from twilio.rest import Client


# ---------------------------------------------------
# LOAD ENV VARIABLES
# ---------------------------------------------------
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

SLACK_WEBHOOK_URL = os.getenv(
    "SLACK_WEBHOOK_URL",
    ""
)

TWILIO_ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID",
    ""
)

TWILIO_AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN",
    ""
)

TWILIO_PHONE_NUMBER = os.getenv(
    "TWILIO_PHONE_NUMBER",
    ""
)


# ---------------------------------------------------
# SEND EMAIL
# ---------------------------------------------------
def send_email(
    subject: str,
    body: str
):

    try:

        receivers = [
            "sahadevkadam923@gmail.com"
        ]

        msg = MIMEMultipart()

        msg["From"] = EMAIL_ADDRESS

        msg["To"] = ", ".join(receivers)

        msg["Subject"] = subject

        msg.attach(
            MIMEText(body, "plain")
        )

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_ADDRESS,
            receivers,
            msg.as_string()
        )

        server.quit()

        print("Email notifications sent successfully")

    except Exception as e:

        print("Email Error:", e)


# ---------------------------------------------------
# SEND SLACK MESSAGE
# ---------------------------------------------------
def send_slack_message(message: str):

    try:

        payload = {
            "text": message
        }

        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload
        )

        print(
            "Slack Status:",
            response.status_code
        )

    except Exception as e:

        print("Slack Error:", e)


# ---------------------------------------------------
# SEND SMS
# ---------------------------------------------------
def send_sms(message: str):

    try:

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        receivers = [
            "+919673847622"
        ]

        for number in receivers:

            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )

        print("SMS alerts sent successfully")

    except Exception as e:

        print("SMS Error:", e)


# ---------------------------------------------------
# MAIN NOTIFICATION FUNCTION
# ---------------------------------------------------
def send_notification(
    channel: str,
    message: str
):

    print(f"[{channel}] {message}")

    # EMAIL ALERT
    send_email(
        "IMS Incident Alert",
        message
    )

    # SLACK ALERT
    send_slack_message(message)

    # SMS ALERT
    send_sms(message)