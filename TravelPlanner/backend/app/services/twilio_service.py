# backend/app/services/twilio_service.py

from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Load credentials from .env file
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_verification_code(phone_number):
    verification = client.verify.services(TWILIO_VERIFY_SERVICE_SID).verifications.create(
        to=phone_number,
        channel="sms"
    )
    return verification.status

def check_verification_code(phone_number, code):
    verification_check = client.verify.services(TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
        to=phone_number,
        code=code
    )
    return verification_check.status == "approved"

def send_sms(phone_number, message):
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid
