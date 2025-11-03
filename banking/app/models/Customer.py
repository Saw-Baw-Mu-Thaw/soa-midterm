from sqlmodel import Field, SQLModel
from pydantic import BaseModel

# DTO will be used by repo to perform CRUD on DB

MAX_DIGIT_11 = 99999999999
MAX_DIGIT_12 = 999999999999
MAX_DIGIT_15 = 999999999999999

class Customers_DTO(SQLModel, table = True):

    __tablename__ = 'customer'

    customer_id : int | None = Field(default=None, primary_key=True)
    student_id : str = Field(default=None, unique=True)
    username : str = Field(default=None, unique=True)
    password_hash : str = Field(default=None)
    full_name : str = Field(default=None)
    phone_number : str = Field(default=None)
    email : str = Field(default=None, unique=True)
    available_balance : int = Field(default=0)
    program : str = Field(default=None)

# This class will be used to transfer and access data

class Customer(BaseModel):
    customer_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    student_id : str | None = Field(max_length=8, min_length=8)
    username : str | None = Field(max_length=50)
    password_hash : str | None = Field(max_length=200, min_length=1)
    full_name : str | None = Field(max_length=50, min_length=1)
    phone_number : str | None = Field(max_length=10, min_length=10)
    email : str | None = Field(max_length=50, min_length=1)
    available_balance : int | None = Field(le = MAX_DIGIT_15)
    program : str | None = Field(max_length=50, min_length=1)