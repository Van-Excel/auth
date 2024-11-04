from datetime import datetime
from typing import Union
from app.response.base import BaseResponse
from pydantic import EmailStr

class RegisterUserResponse(BaseResponse):
    id: int
    name:str
    email:EmailStr
    is_active: bool
    created_at: Union[str, None, datetime] = None

