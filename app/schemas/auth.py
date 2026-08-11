from pydantic import EmailStr
from sqlmodel import SQLModel


class UserSignupRequest(SQLModel):
    email: EmailStr
    password: str
    nickname: str


class UserSignupResponse(SQLModel):
    nickname: str


class UserLoginRequest(SQLModel):
    email: str
    password: str


class UserLoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"