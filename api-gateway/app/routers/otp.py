from fastapi import APIRouter, Depends, HTTPException, status
import requests
from ..repository import config
from typing import Annotated
from ..dependencies import verify_token, get_username
from ..repository import Cust_Repo
import json
from pydantic import BaseModel, Field


router = APIRouter(
    prefix='/otp',
    tags=['otp'],
    dependencies=[Depends(verify_token)]
)

class OTPInput(BaseModel):
    transaction_id : int = Field(gt=0)
    otp : str = Field(min_length=6, max_length=6)

@router.post('/verify')
def verify_otp(input : OTPInput, username : Annotated[str, Depends(get_username)]):
    url = config.OTP_URL + '/otp/verify'
    data = {'transaction_id' : input.transaction_id, 'otp_code' : input.otp}
    response = requests.post(url=url, data=json.dumps(data))

    if response.status_code == 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={'Invalid OTP'}
        )
    elif response.status_code == 410:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={'OTP expired or doesn\'t exist'}
        )
    elif response.status_code == 429:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts"
        )
    
    if response.status_code == 200:
        # Send confirmation email
        cust = Cust_Repo.get_cust_info_by_username(username)

        # complete the transaction
        url = config.BANKING_URL + 'banking/transaction/complete/' + str(input.transaction_id)
        r = requests.put(url=url)

        if r.status_code == 200:
            # send the completion email
            url = config.EMAIL_URL + 'confirm'
            data = {
                'transaction_id' : input.transaction_id,
                'email' : cust.email,
                'customer_name' : cust.full_name
            }
            r = requests.post(url=url, data=json.dumps(data))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incorrect Transaction ID'
            )

@router.get('/resend/{transaction_id}')
def resend_otp(transaction_id : int, username : Annotated[str, Depends(get_username)]):
    cust = Cust_Repo.get_cust_info_by_username(username)

    url = config.OTP_URL + 'otp/resend'
    data = {'transaction_id' : transaction_id}
    r = requests.post(url=url, data=json.dumps(data))

    response = r.json()

    if response['success'] == True:
        url = config.EMAIL_URL + 'send-otp'
        data = {
            'transaction_id' : transaction_id,
            'email' : cust.email,
            'otp_code' : response['data']['otp_code'],
            'Customer_name' : cust.full_name
                }
        
        email_res = requests.post(url=url, data=json.dumps(data))

        if email_res.status_code == 200:
            return {
                'msg' : 'A new otp code has been sent to your email'
            }

    