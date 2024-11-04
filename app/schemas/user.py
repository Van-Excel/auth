from pydantic import BaseModel, EmailStr

class RegisterUserRequest(BaseModel):
    name:str
    email:EmailStr
    password: str

    class Config:
        orm_mode = True


class LoginUser(BaseModel):
    email:str
    password:str

    class Config:
        orm_mode = True


