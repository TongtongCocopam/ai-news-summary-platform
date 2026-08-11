from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import hash_password
from app.exceptions.base import AppException
from app.exceptions.error_code import ErrorCode
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLoginRequest, UserLoginResponse
from app.schemas.auth import UserSignupRequest, UserSignupResponse
from app.core.security import verify_password, create_access_token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def signup(self, request: UserSignupRequest) -> UserSignupResponse:
        async with self.session.begin():
            existing_user = await self.user_repository.find_by_email(
                request.email
            )

            if existing_user is not None:
                raise AppException(ErrorCode.USER_ALREADY_EXISTS, request.email)

            user = User(
                email=request.email,
                password_hash=hash_password(request.password),
                nickname=request.nickname,
            )

            await self.user_repository.save(user)

        return UserSignupResponse(
            nickname=user.nickname
        )

    async def login(self,
                    request: UserLoginRequest
                    ) -> UserLoginResponse:
        user = await self.user_repository.find_by_email(
            request.email
        )

        if user is None:
            raise AppException(
                ErrorCode.INVALID_CREDENTIALS
            )

        if not verify_password(
                request.password,
                user.password_hash,
        ):
            raise AppException(
                ErrorCode.INVALID_CREDENTIALS
            )

        if user.id is None:
            raise AppException(ErrorCode.INTERNAL_SERVER_ERROR)

        access_token = create_access_token(user.id)

        return UserLoginResponse(
            access_token=access_token,
        )