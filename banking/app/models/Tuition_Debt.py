from sqlmodel import Field, SQLModel
from datetime import datetime
from pydantic import BaseModel

# DTO will be used by repo to perform CRUD on DB

MAX_DIGIT_11 = 99999999999
MAX_DIGIT_12 = 999999999999
MAX_DIGIT_15 = 999999999999999

class Tuition_Debt_DTO(SQLModel, table = True):

    __tablename__ = 'tuition_debt'

    debt_id : int | None = Field(default=None, primary_key=True)
    student_id : str | None = Field(default=None)
    amount : int | None = Field(default=0)
    semester : str | None = Field(default=None)
    academic_year : str | None = Field(default=None)
    status : str | None = Field(default="UNPAID")
    due_date : datetime = Field(default=None)
    paid_date : datetime = Field(default=None)
    created_at : datetime | None = Field(default=datetime.now())
    updated_at : datetime = Field(default=None)
    full_name : str | None = Field(default=None)
    program : str | None = Field(default=None)
    

# This class will be used to transfer and access data

class Tuition_Debt(BaseModel):
    debt_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    student_id : str | None = Field(max_length=8, min_length=8)
    amount : int | None = Field(default=0, le=MAX_DIGIT_12)
    semester : str | None = Field(max_length=20)
    academic_year : str | None = Field(max_length=10)
    status : str | None = Field(default = "UNPAID", max_length=10)
    due_date : datetime | None = None
    paid_date : datetime | None = None
    created_at : datetime | None = None
    updated_at : datetime | None = None
    full_name : datetime | None = None
    program : str | None = None