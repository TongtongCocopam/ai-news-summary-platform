from fastapi import APIRouter, status

from app.common.response import ApiResponse
from app.db.session import SessionDep
from app.schemas.auth import UserSignupRequest, UserSignupResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup",
             status_code=status.HTTP_201_CREATED,
             response_model=ApiResponse[UserSignupResponse])
async def signup(request: UserSignupRequest,
                 session:SessionDep):
    service = AuthService(session)

    result = await service.signup(request)

    return ApiResponse(
        success=True,
        data=result,
        error=None
    )
