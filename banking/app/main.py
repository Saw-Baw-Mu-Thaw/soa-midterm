from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from .repository import Transactions_Repo, Debt_Repo, Cust_Repo
from .models.input_models import New_Trans_Input, Fail_Trans_Input
import time

TRANSACTION_EXPIRE_TIME = 5 * 60

app = FastAPI()

@app.get('/')
def root():
    return {'msg' : 'This is the banking service'}

@app.get('/banking/payer/{username}')
def get_customer_by_name(username : str):
    customer = Cust_Repo.get_cust_info_by_username(username)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer with username doesn't exist")
    return customer

@app.get('/banking/receiver/{student_id}')
def get_customer_by_student_id(student_id : str):

    debt = Debt_Repo.get_debt(student_id)

    if debt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer with student id not found")

    response = {'Debt' : debt.model_dump()}

    return response

@app.post('/banking/transaction/create', status_code=status.HTTP_200_OK)
def create_new_transaction(input : New_Trans_Input, backgroundTasks : BackgroundTasks):
    trans_id = Transactions_Repo.create_new_transaction(input.payer_id, input.receiver_id, input.debt_id)
    if trans_id == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Please check your input')
    
    backgroundTasks.add_task(transaction_expiry_timer, trans_id)
    return {'transaction_id' : trans_id}

@app.get('/banking/transaction/{username}')
def get_pending_transaction(username : str):
    transaction = Transactions_Repo.get_pending_transaction(username)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Transaction started by user {username} not found')
    return transaction

@app.get('/banking/receiver/check/{student_id}', description = "Check if anyone has started a transaction for receiver")
def check_pending_transaction(student_id : str):
    result = Transactions_Repo.check_pending_transaction(student_id)
    if(result):
        return {'result' : True}
    return {'result' : False}

@app.put('/banking/transaction/complete/{transaction_id}')
def complete_transaction(transaction_id : int):
    result = Transactions_Repo.complete_transaction(transaction_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please check your input")
    
@app.post('/banking/transaction/fail/')
def fail_transaction(input : Fail_Trans_Input):
    result = Transactions_Repo.fail_transaction(input.transaction_id, input.reason)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please check transaction id")
    
@app.get('/banking/transactions/all/{username}')
def get_all_transactions(username : str):
    transactions = Transactions_Repo.get_all_transaction(username)
    return transactions

def transaction_expiry_timer(transaction_id : int):
    # will wait for 50 seconds
    time.sleep(TRANSACTION_EXPIRE_TIME)

    Transactions_Repo.fail_transaction(transaction_id=transaction_id, reason="Transaction Expired")