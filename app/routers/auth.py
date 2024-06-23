from fastapi import APIRouter, Depends, Response, status, Body
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Union, Optional
from logging import getLogger

from app.schemes import user as user_scheme
from app.schemes import token as token_scheme
from app.schemes import res_msg as msg_scheme
from app.cruds import auth as user_crud
from app.utils import pwd
from app.utils import jwt
from app.utils import error
from app.db import get_db


router = APIRouter()

logger = getLogger("uvicorn")

bearer_scheme = HTTPBearer()

@router.get("/api/auth/me", response_model=user_scheme.ResponseUser, dependencies=[Depends(bearer_scheme)])
async def user_account(user:user_scheme.ResponseUser = Depends(jwt.get_current_user)):
    return user


@router.patch("/api/auth/me", response_model=Union[user_scheme.ResponseUser, msg_scheme.Successful], dependencies=[Depends(bearer_scheme)])
async def edit_account(user:user_scheme.ModifyUser, user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    user = await user_crud.edit_user(db,user,user_id)
    if not user:
        return {"message":"No Alteration."}
    return user


@router.patch("/api/auth/me/reset_pwd", response_model=user_scheme.ResponseUser)
async def edit_account_without_pass(password:str = Body(), user_id:int = Body(), db:AsyncSession = Depends(get_db)):
    hashed_password = pwd.get_password_hash(password)
    return await user_crud.reset_pwd_user(db,user_id,hashed_password)


@router.delete("/api/auth/me", status_code=204, dependencies=[Depends(bearer_scheme)])
async def remove_account(user_id:int = Depends(jwt.get_current_user_id), db:AsyncSession = Depends(get_db)):
    await user_crud.delete_user(db,user_id)
    return


@router.post("/api/auth/registration",response_model=Union[user_scheme.ResponseUser,msg_scheme.Erroneous], status_code=201)
async def create_account(account_body: user_scheme.SignUpUser, response:Response, db:AsyncSession = Depends(get_db)):
    account_body.password = pwd.get_password_hash(account_body.password)
    try:
        user = await user_crud.create_user(db,account_body)
    except error.DuplicateError: 
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error":"Email or username has been already enrolled."}

    if user:
        return user
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error":"We failed to create your account"}
    

@router.post("/api/auth/login",response_model=Union[token_scheme.Token,msg_scheme.Erroneous])
async def sign_account(account_body: user_scheme.SignInUser, response:Response, db:AsyncSession = Depends(get_db)):
    user = await jwt.authenticate_user(account_body,db)

    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error":"Email or password was incorrect."}
    
    access_token =  jwt.create_access_token({"sub":user.email})
    logger.info(access_token)
    return token_scheme.Token(access_token=access_token,token_type="bearer")

