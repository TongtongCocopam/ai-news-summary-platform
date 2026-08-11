from fastapi import APIRouter, Query

from app.common.response import ApiResponse
from app.schemas.trend import TrendItemResponse
from app.dependencies.services import TrendServiceDep


router = APIRouter(
    prefix="/trends",
    tags=["trends"],
)


@router.get(
    "",
    response_model=ApiResponse[list[TrendItemResponse]],
)
async def get_trends(
    trend_service: TrendServiceDep,
    time_window: str = Query(default="24h"),
    limit: int = Query(default=10, ge=1, le=100),
) -> ApiResponse[list[TrendItemResponse]]:

    result = await trend_service.get_hot_trends(
        time_window=time_window,
        limit=limit,
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )