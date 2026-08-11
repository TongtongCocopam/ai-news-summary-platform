from datetime import date, datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text


class Issue(SQLModel, table=True):
    __tablename__ = "issues"

    id: int | None = Field(default=None, primary_key=True)

    category_id: int = Field(
        foreign_key="categories.id",
        index=True,
    )

    issue_date: date = Field(
        default_factory=date.today,
        index=True,
    )

    title: str = Field(max_length=255)

    summary: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    image_url: str | None = Field(
        default=None,
        max_length=1000,
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
    )