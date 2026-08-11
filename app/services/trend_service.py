from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.trend_repository import TrendRepository
from app.schemas.trend import TrendItemResponse


class TrendService:
    def __init__(self, session: AsyncSession):
        self.trend_repository = TrendRepository(session)

    async def get_hot_trends(
        self,
        time_window: str = "24h",
        limit: int = 10,
    ) -> list[TrendItemResponse]:

        rows = await self.trend_repository.find_hot_trends(
            time_window=time_window,
            limit=limit,
        )

        return [
            TrendItemResponse(
                keyword=topic.name,
                trend_score=metric.score,
                mention_count=metric.mention_count,
                outlet_diversity=metric.unique_sources,
            )
            for topic, metric in rows
        ]