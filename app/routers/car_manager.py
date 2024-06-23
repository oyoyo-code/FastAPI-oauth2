from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from logging import getLogger
from typing import List, Union

from app.cruds import car as car_crud
from app.schemes import car as car_scheme
from app.schemes import res_msg as msg_scheme
from app.db import get_db
from app.utils import jwt
from app.utils import error

logger = getLogger("uvicorn")

bearer_scheme = HTTPBearer()

router = APIRouter(
        prefix="/api/cars",
        dependencies=[Depends(jwt.verify_token), Depends(bearer_scheme)],
        responses={401:{"description":"Not Authorized"}}
    )


@router.get("/",response_model=List[car_scheme.ResponseCar])
async def cars(user_id:int = Depends(jwt.get_current_user_id) ,db:AsyncSession = Depends(get_db)):
    return await car_crud.get_active_cars(db, user_id)
# 複数所有を考慮できてる？


@router.post("/",response_model=car_scheme.ResponseCar,status_code=201)
async def create_car(car_body: car_scheme.EnrollCar, db: AsyncSession = Depends(get_db), user_id:int = Depends(jwt.get_current_user_id)):
    dict_car_body = dict(car_body)
    dict_car_body.update({"user_id":user_id})
    entire_car_info = car_scheme.CreateCar(**dict_car_body)
    try:
        car = await car_crud.create_active_car(db,entire_car_info)
    except error.DuplicateError:
        raise HTTPException(status_code=400,detail="The car has been already enrolled.")
    return car


@router.get("/{car_id}",response_model=car_scheme.ResponseCar)
async def car(car_id:int,db:AsyncSession = Depends(get_db)):
    try:
        car = await car_crud.get_active_car(db,car_id)
    except error.NoObjectError:
        raise HTTPException(status_code=404)
    return car
# カスタムエラーはHTTPExceptionに統一するべき。後で取り組みたい。

@router.patch("/{car_id}",response_model=Union[car_scheme.ResponseCar,msg_scheme.Successful])
async def edit_car(car_id:int, car_body:car_scheme.ModifyCar,db:AsyncSession = Depends(get_db)):
    car = await car_crud.edit_active_car(db, car_body, car_id)
    if not car:
        return {"message":"No Alteration."}
    return car


@router.delete("/{car_id}", status_code=204)
async def eliminate_car(car_id:int, db: AsyncSession = Depends(get_db)):
    await car_crud.delete_active_car(db,car_id)
    return
