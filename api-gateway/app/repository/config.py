import os
from dotenv import load_dotenv

load_dotenv()

# Connection String of DATABASE named "ibanking_db"
DATABASE_URL = os.getenv("DATABASE_URL","mysql+pymysql://root:@localhost:3306/ibanking_db?charset=utf8mb4")

SECRET_KEY = os.getenv("SECRET_KEY", "MY_SUPER_SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

BANKING_URL = os.getenv("BANKING_URL", "http://127.0.0.1:8001/")
OTP_URL = os.getenv("OTP_URL", "http://127.0.0.1:8002/")
EMAIL_URL = os.getenv("EMAIL_URL", "http://127.0.0.1:8003/")