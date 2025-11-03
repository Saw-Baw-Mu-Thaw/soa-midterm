from fastapi import APIRouter, HTTPException, Depends, Path, status
import requests
from ..repository import config
from typing import Annotated
from ..dependencies import verify_token
from ..models.Customer import Customer

router = APIRouter(
    prefix='/customers',
    tags = ['Customers'],
    dependencies=[Depends(verify_token)]
)

@router.get('/payer/{username}')
def get_customer_by_username(username : str):
    url = config.BANKING_URL + '/banking/payer/' + username
    response = requests.get(url=url)
    r = response.json()

    if response.status_code == 200:
        cust = Customer(**r)
        return cust
    else:
        return r

@router.get('/receiver/{student_id}')
def get_receiver_info(student_id : str):
    url = config.BANKING_URL + '/banking/receiver/' + student_id
    response = requests.get(url=url)
    if response.status_code == 200:
        r = response.json()
        return r
    elif response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Student does not exist'
        )

@router.get('/receiver/check/{receiver_id}', description="Check if anyone has started a transaction for receiver")
def check_pending_transaction(receiver_id : Annotated[str, Path(description='The student ID of the receiver')]):
    url = config.BANKING_URL + '/banking/receiver/check/' + receiver_id
    response = requests.get(url=url)
    r = response.json()
    return r