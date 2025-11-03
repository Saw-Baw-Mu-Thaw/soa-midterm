#main.py
from fastapi import FastAPI
import uvicorn
from .router import otp_routers

app = FastAPI()

#Router for OTP Service
app.include_router(otp_routers.router)

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8002)
