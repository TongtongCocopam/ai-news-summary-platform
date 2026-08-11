from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import hash_password
from app.exceptions.base import AppException
from app.exceptions.error_code import ErrorCode
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserSignupRequest, UserSignupResponse


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def signup(self, request: UserSignupRequest) -> UserSignupResponse:
        existing_user = await self.user_repository.find_by_email(
            request.email
        )

        if existing_user:
            raise AppException(ErrorCode.USER_ALREADY_EXISTS, request.email)

        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            nickname=request.nickname,
        )

        async with self.session.begin():
            await self.user_repository.save(user)

        return UserSignupResponse(
            nickname=user.nickname
        )
