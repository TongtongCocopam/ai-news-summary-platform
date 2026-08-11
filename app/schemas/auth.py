from pydantic import EmailStr
from sqlmodel import SQLModel


class UserSignupRequest(SQLModel):
    email: EmailStr
    password: str
    nickname: str


class UserSignupResponse(SQLModel):
    nickname: str