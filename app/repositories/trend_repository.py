from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.topic import Topic, TopicMetric


class TrendRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_hot_trends(
        self,
        time_window: str,
        limit: int,
    ):
        statement = (
            select(Topic, TopicMetric)
            .join(
                TopicMetric,
                col(TopicMetric.topic_id) == col(Topic.id),
            )
            .where(
                col(TopicMetric.metric_type) == "hotness",
                col(TopicMetric.time_window) == time_window,
            )
            .order_by(
                col(TopicMetric.score).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.all()