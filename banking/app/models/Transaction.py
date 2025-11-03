from sqlmodel import Field, SQLModel
from datetime import datetime
from pydantic import BaseModel

MAX_DIGIT_11 = 99999999999
MAX_DIGIT_12 = 999999999999
MAX_DIGIT_15 = 999999999999999


# DTO will be used by repo to perform CRUD on DB

class Transactions_DTO(SQLModel, table = True):

    __tablename__ = 'transactions'

    transaction_id : int | None = Field(default=None, primary_key=True)
    payer_id : int | None = Field(default=None, foreign_key='customer.customer_id')
    receiver_id : str | None = Field(default=None, foreign_key='customer.student_id')
    debt_id : int | None = Field(default=None, foreign_key='tuition_debt.debt_id')
    amount : int | None = Field(default=None)
    status : str | None = Field(default='PENDING')
    initiated_at : datetime | None = Field(default=None)
    completed_at : datetime | None = Field(default=None)
    failure_reason : str | None = Field(default=None)

# This class will be used to transfer and access data

class Transaction(BaseModel):
    transaction_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    payer_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    receiver_id : str | None = Field(max_length=8, min_length=8)
    debt_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    amount : int | None = Field(default=0, le=MAX_DIGIT_12)
    status : str | None = Field(default='PENDING', max_length=20)
    initiated_at : datetime | None = None
    completed_at : datetime | None = None
    failure_reason : str | None = Field(default=None, max_length=100)

