from datetime import datetime

from sqlmodel import SQLModel


class IssueResponse(SQLModel):
    id: int
    category_name: str
    title: str
    summary: str
    image_url: str | None
    created_at: datetime