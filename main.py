from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import functions

app = FastAPI()
load_dotenv()


@app.get("/", name="Hello, World!")
def hello_world():
    return {"message": f"Hello, World! From {os.getenv('SERVICE_NAME')}"}


class Phone(BaseModel):
    phone_number: str


@app.post("/auth/send_auth_code")
def phone_(phone: Phone):
    phone_number = "".join([c for c in phone.phone_number if c.isnumeric()])
    functions.send_sms(phone_number, "The Code is 1234")
