from typing import Union
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemes import user

class BaseCar(BaseModel):
    buy_num: int = Field(ge=1)
    car_name: str = Field(..., example="silvia s13")
    created_at: datetime = Field(default=datetime.now())
    sold_at: datetime = Field(default=None)
    comment: Union[str, None] = None

class EnrollCar(BaseCar):
    pass

class ModifyCar(BaseModel):
    buy_num: Union[int, None] = Field(default=None,ge=1)
    car_name: Union[str, None] = Field(default=None)
    created_at: Union[datetime, None] = Field(default=None)
    sold_at: Union[datetime, None] = Field(default=None)
    comment: Union[str, None] = Field(default=None)

class CreateCar(BaseCar):
    user_id: int = Field(ge=1)

class DataBaseCar(CreateCar):
    id: int = Field(ge=1)

class ResponseCar(DataBaseCar,user.ConcatUserFromCar):
    pass

class Config:
    orm_mode = True
