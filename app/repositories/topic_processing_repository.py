from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.article import Article, ArticleSummary
from app.models.topic import (
    Topic,
    ArticleTopic,
    TopicMetric,
)


class TopicProcessingRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_unprocessed_summaries(
        self,
        limit: int = 500,
    ) -> list[ArticleSummary]:

        statement = (
            select(ArticleSummary)
            .where(
                col(ArticleSummary.topic_processed_at).is_(None)
            )
            .order_by(
                col(ArticleSummary.id)
            )
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def find_topics_by_names(
        self,
        names: set[str],
    ) -> list[Topic]:

        if not names:
            return []

        statement = (
            select(Topic)
            .where(
                col(Topic.name).in_(names)
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def find_existing_assignments(
        self,
        article_ids: set[int],
    ) -> set[tuple[int, int]]:

        if not article_ids:
            return set()

        statement = (
            select(
                ArticleTopic.topic_id,
                ArticleTopic.article_id,
            )
            .where(
                col(ArticleTopic.article_id).in_(article_ids)
            )
        )

        result = await self.session.execute(statement)

        return {
            (topic_id, article_id)
            for topic_id, article_id in result.all()
        }

    async def aggregate_topics(
        self,
        start: datetime,
        end: datetime,
    ):
        statement = (
            select(
                ArticleTopic.topic_id,
                func.count().label("mention_count"),
                func.count(
                    func.distinct(Article.source_id)
                ).label("unique_sources"),
            )
            .join(
                Article,
                col(Article.id)
                == col(ArticleTopic.article_id),
            )
            .where(
                col(Article.published_at) >= start,
                col(Article.published_at) < end,
            )
            .group_by(
                ArticleTopic.topic_id
            )
        )

        result = await self.session.execute(statement)

        return result.all()

    async def find_metrics(
        self,
        topic_ids: list[int],
    ) -> list[TopicMetric]:

        if not topic_ids:
            return []

        statement = (
            select(TopicMetric)
            .where(
                col(TopicMetric.topic_id).in_(topic_ids),
                col(TopicMetric.metric_type) == "hotness",
                col(TopicMetric.time_window) == "24h",
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    def add_all(
        self,
        objects: list,
    ) -> None:
        self.session.add_all(objects)