from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.source import Source


class SourceRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def find_by_names(
        self,
        names: set[str],
    ) -> list[Source]:

        if not names:
            return []

        statement = (
            select(Source)
            .where(
                col(Source.name).in_(names)
            )
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    def add_all(
        self,
        sources: list[Source],
    ) -> None:
        self.session.add_all(sources)