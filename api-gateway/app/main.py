from fastapi import FastAPI, Depends, HTTPException, status
from .repository import config
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pydantic import BaseModel
from .dependencies import convert_to_customer
from .models.Customer import Customer
from .repository import Cust_Repo
from .routers import customers, transactions, otp
from fastapi.middleware.cors import CORSMiddleware

ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

class Token(BaseModel):
    access_token : str
    token_type : str

# for User class, we instead use Customer

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data : dict, expires_delta : timedelta):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({'exp' : expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def get_user(username : str):
    user = Cust_Repo.get_cust_info_by_username(username)

    if user is None:
        return None
    
    user = convert_to_customer(user)
    return user



async def get_current_active_user(token : Annotated[str, Depends(oauth2_scheme)]):
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
    
    user = get_user(username)
    return user
                

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*', 'localhost'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(otp.router)

@app.post('/token', response_model=Token, tags=['Login'])
async def login_for_access_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub' : user.username}, expires_delta= access_token_expire)

    return {'access_token' : access_token, 'token_type' : 'bearer'}

@app.get('/customers/me', response_model=Customer, tags=['Login'])
async def get_current_user(current_user : Annotated[Customer, Depends(get_current_active_user)]):
    return current_user

