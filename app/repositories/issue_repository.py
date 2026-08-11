from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.category import Category
from app.models.issue import Issue


class IssueRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_recent(
        self,
        since: datetime,
        limit: int,
    ) -> list[tuple[Issue, Category]]:

        statement = (
            select(Issue, Category)
            .join(
                Category,
                col(Issue.category_id) == col(Category.id),
            )
            .where(
                col(Issue.created_at) >= since
            )
            .order_by(
                col(Issue.created_at).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return [
            (issue, category)
            for issue, category in result.all()
        ]

    async def find_by_id(
        self,
        issue_id: int,
    ) -> tuple[Issue, Category] | None:

        statement = (
            select(Issue, Category)
            .join(
                Category,
                col(Issue.category_id) == col(Category.id),
            )
            .where(
                col(Issue.id) == issue_id
            )
        )

        result = await self.session.execute(statement)

        row = result.first()

        if row is None:
            return None

        issue, category = row

        return issue, category