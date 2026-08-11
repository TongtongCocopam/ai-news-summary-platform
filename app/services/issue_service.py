from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import AppException
from app.exceptions.error_code import ErrorCode
from app.repositories.issue_repository import IssueRepository
from app.schemas.issue import IssueResponse


class IssueService:

    def __init__(self, session: AsyncSession):
        self.issue_repository = IssueRepository(session)

    async def get_recent_issues(
        self,
        limit: int = 3,
    ) -> list[IssueResponse]:

        since = datetime.now() - timedelta(hours=24)

        rows = await self.issue_repository.find_recent(
            since=since,
            limit=limit,
        )

        return [
            IssueResponse(
                id=issue.id,
                category_name=category.name,
                title=issue.title,
                summary=issue.summary,
                image_url=issue.image_url,
                created_at=issue.created_at,
            )
            for issue, category in rows
        ]

    async def get_issue(
        self,
        issue_id: int,
    ) -> IssueResponse:

        row = await self.issue_repository.find_by_id(
            issue_id
        )

        if row is None:
            raise AppException(
                ErrorCode.ISSUE_NOT_FOUND
            )

        issue, category = row

        return IssueResponse(
            id=issue.id,
            category_name=category.name,
            title=issue.title,
            summary=issue.summary,
            image_url=issue.image_url,
            created_at=issue.created_at,
        )