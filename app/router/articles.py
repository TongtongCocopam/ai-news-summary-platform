from fastapi import APIRouter, Query

from app.common.response import ApiResponse
from app.dependencies.services import ArticleServiceDep
from app.schemas.article import (
    ArticleDetailResponse,
    ArticleItemResponse,
    RelatedArticleResponse,
)


router = APIRouter(
    prefix="/articles",
    tags=["articles"],
)


@router.get(
    "/corrections",
    response_model=ApiResponse[list[ArticleItemResponse]],
)
async def get_corrections(
    article_service: ArticleServiceDep,
    since_hours: int = Query(
        default=48,
        ge=1,
    ),
    limit: int = Query(
        default=3,
        ge=1,
        le=100,
    ),
) -> ApiResponse[list[ArticleItemResponse]]:

    result = await article_service.get_corrections(
        since_hours=since_hours,
        limit=limit,
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )


@router.get(
    "",
    response_model=ApiResponse[list[ArticleItemResponse]],
)
async def search_articles(
    article_service: ArticleServiceDep,
    q: str = Query(
        min_length=1,
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

    result = await article_service.search_articles(
        keyword=q,
        offset=offset,
        limit=limit,
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )


@router.get(
    "/{article_id}/related",
    response_model=ApiResponse[list[RelatedArticleResponse]],
)
async def get_related_articles(
    article_id: int,
    article_service: ArticleServiceDep,
    limit: int = Query(
        default=3,
        ge=1,
        le=20,
    ),
) -> ApiResponse[list[RelatedArticleResponse]]:

    result = await article_service.get_related_articles(
        article_id=article_id,
        limit=limit,
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )


@router.get(
    "/{article_id}",
    response_model=ApiResponse[ArticleDetailResponse],
)
async def get_article(
    article_id: int,
    article_service: ArticleServiceDep,
) -> ApiResponse[ArticleDetailResponse]:

    result = await article_service.get_article(
        article_id
    )

    return ApiResponse(
        success=True,
        data=result,
        error=None,
    )