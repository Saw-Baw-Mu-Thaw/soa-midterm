import requests
from fastapi import APIRouter, Depends, HTTPException, status, Path
from ..dependencies import verify_token, get_username, verify_receiver
from ..models.input_models import NewTransactionInput
from typing import Annotated
from ..repository import config, Cust_Repo
import json

router = APIRouter(
    prefix='/transactions',
    tags=['Transactions'],
    dependencies=[Depends(verify_token)]
)

@router.post('/create', description='Create a new transaction')
async def create_new_transaction(input : NewTransactionInput, username : Annotated[str, Depends(get_username)]):
    # verify receiver
    verify_receiver(input.receiver_id)

    # verify payer
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='One or more incorrect input')
    
    # check balance >= tuition
    if input.available_balance < input.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Insufficient balance')
    
    # check any pending transaction
    url = config.BANKING_URL + 'banking/receiver/check/' + input.receiver_id
    response = requests.get(url=url)

    r = response.json()

    if r['result'] == True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pending Transaction')
    
    
    # then create new transaction
    url = config.BANKING_URL + 'banking/transaction/create'
    data = {
        'payer_id' : input.payer_id,
        'receiver_id' : input.receiver_id.upper(),
        'debt_id' : input.debt_id
            }
    response = requests.post(url=url, data=json.dumps(data))

    if response.status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Please check your input')
    
    r = response.json()
    transaction_id = r['transaction_id']

    # TODO : send transaction id to otp service
    otp_resp = requests.post(
        f"{config.OTP_URL}otp/generate",
        json={"transaction_id": transaction_id},
        timeout=20
    )

    if otp_resp.status_code != 200:
        return {
            "success": True,
            "message": "Transaction created. OTP failed — use /otp/resend",
            "transaction_id": transaction_id,
            "error": otp_resp.text
        }

    otp_json = otp_resp.json()
    otp_code = otp_json["data"]["otp_code"]  
    expires_in = otp_json["data"]["expires_in_seconds"]

    payer = Cust_Repo.get_cust_info_by_username(username)
    customer_email = payer.email or "test@example.com"
    customer_name = payer.full_name or "Customer"

    #TODO : send request to email service
    email_payload = {
        "transaction_id": transaction_id,
        "email": customer_email,
        "otp_code": otp_code,
        "customer_name": customer_name
    }

    try:
        email_resp = requests.post(
            f"{config.EMAIL_URL}send-otp",
            json=email_payload,
            timeout=10
        )
        email_sent = email_resp.status_code == 200
    except:
        email_sent = False

    
    return {
        "success": True,
        "message": "Transaction created & OTP sent to your EMAIL!",
        "transaction_id": transaction_id,
        "otp_sent_to": customer_email,
        "expires_in_seconds": expires_in,
        "email_status": "sent" if email_sent else "failed (check terminal)",
    }

@router.get('/me')
async def get_all_transactions(username : Annotated[str , Depends(get_username)],dependencies=[Depends(verify_token)]):
    url = config.BANKING_URL + 'banking/transactions/all/' + username
    response = requests.get(url=url)
    return response.json()
