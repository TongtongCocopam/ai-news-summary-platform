from datetime import datetime

from sqlmodel import SQLModel

from app.models.fact_check import CheckResultEnum


class ArticleItemResponse(SQLModel):
    id: int
    title: str
    original_title: str
    summary: str | None
    author: str | None
    # image_url: str | None
    outlet: str | None
    url: str
    published_at: datetime | None


class RelatedArticleResponse(ArticleItemResponse):
    similarity_score: float


class FactCheckResponse(SQLModel):
    compared_article_id: int
    similarity_score: float
    check_result: CheckResultEnum

    title: str
    outlet: str | None


class ArticleDetailResponse(ArticleItemResponse):
    fact_checks: list[FactCheckResponse]