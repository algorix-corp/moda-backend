import boto3
from dotenv import load_dotenv
import os
import random

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def send_sms(phone, text):
    if phone[0] != "+":
        phone = "+82" + phone[1:]

    client = boto3.client(
        "sns",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="us-east-1",
    )

    client.publish(
        PhoneNumber=phone,
        Message=text,
    )

    print(f"Sent SMS to {phone} with text: {text}")


def make_auth_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])
