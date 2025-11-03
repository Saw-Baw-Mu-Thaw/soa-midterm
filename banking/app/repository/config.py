import os
from dotenv import load_dotenv

load_dotenv()

# Connection String of DATABASE named "ibanking_db"
DATABASE_URL = os.getenv("DATABASE_URL","mysql+pymysql://root:@localhost:3306/ibanking_db?charset=utf8mb4")

