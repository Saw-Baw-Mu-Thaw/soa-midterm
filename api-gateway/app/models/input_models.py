from pydantic import BaseModel, Field

MAX_DIGIT_11 = 99999999999
MAX_DIGIT_12 = 999999999999
MAX_DIGIT_15 = 999999999999999

class NewTransactionInput(BaseModel):
    payer_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    receiver_id : str | None = Field(max_length=8, min_length=8)
    debt_id : int | None = Field(gt=0, le=MAX_DIGIT_11)
    amount : int | None = Field(default=0, le=MAX_DIGIT_12, description='Tuition amount')
    available_balance : int | None = Field(le = MAX_DIGIT_15, description='Payer\'s balance')

