from fastapi import APIRouter, Query

from app.common.response import ApiResponse
from app.dependencies.services import CategoryServiceDep
from app.schemas.article import ArticleItemResponse
from app.schemas.category import CategoryResponse


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get(
    "",
    response_model=ApiResponse[list[CategoryResponse]],
)
async def get_categories(
    category_service: CategoryServiceDep,
) -> ApiResponse[list[CategoryResponse]]:

    result = await category_service.get_categories()

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )


@router.get(
    "/{category_id}/articles",
    response_model=ApiResponse[list[ArticleItemResponse]],
)
async def get_category_articles(
    category_id: int,
    category_service: CategoryServiceDep,
    subcategory_id: int | None = Query(
        default=None,
        ge=1,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> ApiResponse[list[ArticleItemResponse]]:

    result = await category_service.get_articles(
        category_id=category_id,
        subcategory_id=subcategory_id,
        offset=offset,
        limit=limit,
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )