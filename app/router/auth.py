from fastapi import APIRouter, status

from app.common.response import ApiResponse
from app.dependencies.dependency import AuthServiceDep
from app.schemas.auth import UserLoginResponse, UserLoginRequest
from app.schemas.auth import UserSignupRequest, UserSignupResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup",
             status_code=status.HTTP_201_CREATED,
             response_model=ApiResponse[UserSignupResponse])
async def signup(request: UserSignupRequest,
                 auth_service:AuthServiceDep):

    result = await auth_service.signup(request)

    return ApiResponse(
        success=True,
        data=result,
        error=None
    )

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserLoginResponse],
)
async def login(
    request: UserLoginRequest,
    auth_service: AuthServiceDep,
) -> ApiResponse[UserLoginResponse]:

    result = await auth_service.login(request)

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )