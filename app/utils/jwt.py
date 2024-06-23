from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from jose import jwt, JWTError
from typing import Union
from logging import getLogger

from datetime import datetime, timedelta

from app.schemes import user as user_scheme
from app.schemes import token as token_scheme
from app.cruds import auth as user_crud
from app.utils import pwd
from app.db import get_db

logger = getLogger("uvicorn")

JWT_ALGORITHM = "HS256"
SECRET_KEY = "100687f6eb4b1c8f9c972e28669564d84b41512a9f411e95a95ea857b03f4c2b"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

async def validate_user(email:EmailStr,db:AsyncSession):
    flag = await user_crud.validate_user(db,email)
    return flag


async def get_user(email:EmailStr,db:AsyncSession) -> user_scheme.ResponseUser :
    user = await user_crud.get_user(db,email)
    return user


async def authenticate_user(account_body: user_scheme.SignInUser,db:AsyncSession) -> Union[user_scheme.ResponseUser,False]:
    user = await user_crud.get_user(db,account_body.email)

    if not user or not pwd.verify_password(account_body.password, user.password):
        return False
    
    return user


def create_access_token(data:user_scheme.SignInUser):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=2)

    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


def get_token(token:str = Depends(oauth2_scheme)) -> token_scheme.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception
        token_data = token_scheme.TokenData(email=email)

    except JWTError:
        raise credentials_exception
    
    return token_data.email


async def get_current_user(token_data_email:token_scheme.TokenData = Depends(get_token), db:AsyncSession = Depends(get_db)):
    user = await get_user(token_data_email,db)
    if not user:
        raise credentials_exception
    
    return user


async def get_current_user_id(token_data_email:token_scheme.TokenData = Depends(get_token), db:AsyncSession = Depends(get_db)):
    user = await get_user(token_data_email,db)
    if not user:
        raise credentials_exception
    
    return user.id


async def verify_token(token_data_email:token_scheme.TokenData = Depends(get_token), db:AsyncSession = Depends(get_db)):
    flag = await validate_user(token_data_email, db)
    # verify token 自体は動いている。
    if not flag:
        raise credentials_exception
    
    

