from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.article import (
    Article,
    ArticleSummary,
    ArticleSimilarity,
)
from app.models.source import Source
from app.models.topic import Topic, ArticleTopic
from app.models.fact_check import FactCheckResult


class ArticleRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_ids(
        self,
        keyword: str,
        offset: int,
        limit: int,
    ) -> list[int]:

        pattern = f"%{keyword}%"

        summary_article_ids = (
            select(ArticleSummary.article_id)
            .where(
                or_(
                    col(ArticleSummary.summary_title).like(pattern),
                    col(ArticleSummary.summary_text).like(pattern),
                )
            )
        )

        topic_article_ids = (
            select(ArticleTopic.article_id)
            .join(
                Topic,
                col(ArticleTopic.topic_id) == col(Topic.id),
            )
            .where(
                col(Topic.name).like(pattern)
            )
        )

        statement = (
            select(Article.id)
            .where(
                or_(
                    col(Article.title).like(pattern),
                    col(Article.id).in_(summary_article_ids),
                    col(Article.id).in_(topic_article_ids),
                )
            )
            .order_by(
                col(Article.published_at).desc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def find_articles_with_source(
        self,
        article_ids: list[int],
    ):
        if not article_ids:
            return []

        statement = (
            select(Article, Source)
            .outerjoin(
                Source,
                col(Article.source_id) == col(Source.id),
            )
            .where(
                col(Article.id).in_(article_ids)
            )
        )

        result = await self.session.execute(statement)

        return result.all()

    async def find_summaries(
        self,
        article_ids: list[int],
    ) -> list[ArticleSummary]:

        if not article_ids:
            return []

        statement = (
            select(ArticleSummary)
            .where(
                col(ArticleSummary.article_id).in_(article_ids)
            )
            .order_by(
                col(ArticleSummary.id)
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def find_by_id(
        self,
        article_id: int,
    ):
        statement = (
            select(Article, Source)
            .outerjoin(
                Source,
                col(Article.source_id) == col(Source.id),
            )
            .where(
                col(Article.id) == article_id
            )
        )

        result = await self.session.execute(statement)

        return result.first()

    async def find_fact_checks(
        self,
        article_id: int,
        limit: int = 3,
    ):
        statement = (
            select(
                FactCheckResult,
                Article,
                Source,
            )
            .join(
                Article,
                col(FactCheckResult.compared_article_id)
                == col(Article.id),
            )
            .outerjoin(
                Source,
                col(Article.source_id) == col(Source.id),
            )
            .where(
                col(FactCheckResult.article_id) == article_id
            )
            .order_by(
                col(FactCheckResult.similarity_score).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.all()

    async def find_related(
        self,
        article_id: int,
        limit: int,
    ):
        statement = (
            select(
                ArticleSimilarity,
                Article,
                Source,
            )
            .join(
                Article,
                col(ArticleSimilarity.related_article_id)
                == col(Article.id),
            )
            .outerjoin(
                Source,
                col(Article.source_id) == col(Source.id),
            )
            .where(
                col(ArticleSimilarity.article_id) == article_id
            )
            .order_by(
                col(ArticleSimilarity.similarity_score).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.all()

    async def find_corrections(
        self,
        since: datetime,
        limit: int,
    ):
        statement = (
            select(Article, Source)
            .outerjoin(
                Source,
                col(Article.source_id) == col(Source.id),
            )
            .where(
                col(Article.is_correction).is_(True),
                col(Article.published_at) >= since,
            )
            .order_by(
                col(Article.published_at).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.all()


    async def find_ids_by_category(
            self,
            category_id: int,
            subcategory_id: int | None,
            offset: int,
            limit: int,
    ) -> list[int]:

        statement = (
            select(Article.id)
            .where(
                col(Article.category_id) == category_id
            )
        )

        if subcategory_id is not None:
            statement = statement.where(
                col(Article.subcategory_id) == subcategory_id
            )

        statement = (
            statement
            .order_by(
                col(Article.published_at).desc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(
            result.scalars().all()
        )