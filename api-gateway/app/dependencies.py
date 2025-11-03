from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .repository import config, Cust_Repo
from .models.Customer import Customers_DTO, Customer
import json

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/token')

async def verify_token(token : Annotated[str, Depends(oauth_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate' : 'Bearer'}
    )

    try :
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
def convert_to_customer(input : Customers_DTO):
    content : str = input.model_dump_json()
    decode_result = json.loads(content)
    return Customer(**decode_result)

def verify_receiver(student_id : str):
    input_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='One or more incorrect input'
    )
    if len(student_id) != 8:
        raise input_exception

    receiver = Cust_Repo.get_cust_info_by_id(student_id)

    if receiver is None:
        raise input_exception
    
async def get_username(token : Annotated[str, Depends(oauth_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate' : 'Bearer'}
    )

    try :
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return username
