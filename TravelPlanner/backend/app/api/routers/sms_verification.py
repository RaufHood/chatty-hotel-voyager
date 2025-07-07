# TravelPlanner/backend/app/api/routers/sms_verification.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.twilio_service import send_verification_code, check_verification_code

router = APIRouter()

class PhoneSchema(BaseModel):
    phone_number: str

class VerifySchema(BaseModel):
    phone_number: str
    code: str

@router.post("/send-verification-code")
async def send_code(data: PhoneSchema):
    try:
        status = send_verification_code(data.phone_number)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-code")
async def verify_code(data: VerifySchema):
    try:
        result = check_verification_code(data.phone_number, data.code)
        return {"verified": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
