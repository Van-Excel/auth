from fastapi import APIRouter, status, Depends, Query
from app.schemas.user import RegisterUserRequest, LoginUser
from app.response.users import RegisterUserResponse
from sqlalchemy.orm import Session
from app.config.database import get_session
from app.services.user import create_user, login_user, verify_registered_user
from app.config.email import send_account_verification_email


user_route = APIRouter(
    tags = ['users'],
    prefix = "/users"
)


@user_route.get("/")
async def get_users():
    return {"message":"Welcome"}


@user_route.post("/register", status_code = status.HTTP_201_CREATED, response_model = RegisterUserResponse)
async def register_user(data:RegisterUserRequest, session:Session = Depends(get_session)):
    return await create_user(data, session)

@user_route.get("/verify", status_code= status.HTTP_200_OK)
async def verify_user(email:str, token:str, session:Session= Depends(get_session)):
    return await verify_registered_user(email, session, token) 

@user_route.post("/login", status_code= 201)
async def login_user(data:LoginUser, session:Session=Depends(get_session)):
    # send login data
    # check if you are in a database
    # if true, create access and refresh token and send in response
    response = await login_user(user = data, session= session)
    return response

