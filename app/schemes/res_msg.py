from pydantic import BaseModel, Field

class Successful(BaseModel):
    message:str = Field(default="You succeeded in doing so.", title="Success message.")

class Erroneous(BaseModel):
    error:str = Field(default="Something went wrong.",title="Error message")