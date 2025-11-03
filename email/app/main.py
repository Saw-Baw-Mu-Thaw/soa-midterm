from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from config import SMTP_HOST, SMTP_PASS, SMTP_PORT, SMTP_USER


app = FastAPI(title="Email Service", version="1.0")


class SendOTPRequest(BaseModel):
    transaction_id: int
    email: str
    otp_code: str
    customer_name: str = "Customer"

class ConfirmPaymentRequest(BaseModel):
    transaction_id: int
    email: str
    customer_name: str = "Customer"

def send_email(to_email: str, subject: str, body: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f" Email sent to {to_email}")
        return True
    except Exception as e:
        print(f" Email failed: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Email Service Running!"}

@app.post("/send-otp")
async def send_otp(req: SendOTPRequest):
    subject = f"Your OTP for Transaction #{req.transaction_id}"
    html = f"""
    <h2>Secure Verification</h2>
    <p>Hi {req.customer_name},</p>
    <h1 style="letter-spacing: 5px; color: #4CAF50;"><b>{req.otp_code}</b></h1>
    <p>Valid for 5 minutes.</p>
    <small>Transaction: {req.transaction_id}</small>
    """
    if send_email(req.email, subject, html):
        return {"success": True}
    raise HTTPException(500, "Email failed")

@app.post("/confirm")
async def confirm_payment(req: ConfirmPaymentRequest):
    subject = f" Payment Confirmed - Transaction #{req.transaction_id}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 20px; text-align: center;">
            <h1> Payment Successful!</h1>
        </div>
        
        <div style="padding: 25px; background: #f9f9f9;">
            <p style="font-size: 16px; color: #333;">
                Hi <strong>{req.customer_name}</strong>,
            </p>
            <p>We're thrilled to confirm your payment has been processed successfully!</p>
            <p>Thank you for your trust!</p>
        </div>
    </div>
    """
    
    if send_email(req.email, subject, html):
        return {"success": True, "message": "Confirmation sent!"}
    raise HTTPException(500, "Failed to send confirmation")

if __name__ == "__main__":
    uvicorn.run("email:app", host="127.0.0.1", port=8003, reload=True)