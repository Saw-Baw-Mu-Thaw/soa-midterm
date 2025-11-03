from sqlmodel import Field
from pydantic import BaseModel

MAX_DIGIT_11 = 99999999999

class New_Trans_Input(BaseModel):
    payer_id : int = Field(gt=0, le=MAX_DIGIT_11, description='Customer id of the payer')
    receiver_id : str = Field(max_length=8, min_length=8, description='Student id of the receiver')
    debt_id : int = Field(gt=0, le=MAX_DIGIT_11, description='Debt id of the receiver')

class Fail_Trans_Input(BaseModel):
    transaction_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    reason : str | None = Field(default=None, max_length=100)