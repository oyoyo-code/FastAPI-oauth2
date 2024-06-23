from pydantic import BaseModel, EmailStr, Field
from typing import Union

class BaseUser(BaseModel):
    email: EmailStr

class ConcatUserFromCar(BaseUser):
    username: str = Field(...,min_length=4, max_length=10)

class ServerBaseUser(BaseUser):
    password: str

class FullInfoUser(ServerBaseUser):
    username: str = Field(...,min_length=4, max_length=10)

class SignInUser(ServerBaseUser):
    pass

class SignUpUser(FullInfoUser):
    pass

class ModifyUser(BaseModel):
    email: Union[EmailStr,None] = Field(default=None)
    username: Union[str,None] = Field(default=None, min_length=4, max_length=10)
    password: Union[str, None] = Field(default=None)

class CreateUser(FullInfoUser):
    pass

class DatabaseUser(FullInfoUser):
    id:int = Field(
        ge=1,
        title="User_id",
        description="This id is used to identify what the car managers the user create."
    )

    class Config:
        orm_mode = True

class ResponseUser(BaseUser):
    id:int = Field(
        ge=1,
        title="User_id",
        description="This id is used to identify what the car managers the user create."
    )
    username: str = Field(...,min_length=4, max_length=10)

    class Config:
        orm_mode = True










