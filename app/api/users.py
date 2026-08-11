from fastapi import APIRouter, status

from app.common.response import ApiResponse
from app.dependencies.dependency import UserServiceDep
from app.schemas.auth import UserLoginResponse, UserLoginRequest

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserLoginResponse],
)
async def login(
    request: UserLoginRequest,
    user_service: UserServiceDep,
) -> ApiResponse[UserLoginResponse]:

    result = await user_service.login(request)

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )