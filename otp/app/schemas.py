# schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class OTPGenerateRequest(BaseModel):
    transaction_id: int = Field(..., gt=0)

class OTPGenerateResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None   

class OTPVerifyRequest(BaseModel):
    transaction_id: int = Field(..., gt=0)
    otp_code: str = Field(..., min_length=6, max_length=6)

class OTPVerifyResponse(BaseModel):
    success: bool
    verified: bool
    message: str
    remaining_attempts: Optional[int] = None