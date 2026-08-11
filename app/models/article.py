from datetime import datetime

from sqlalchemy import Column, Text, JSON
from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: int | None = Field(default=None, primary_key=True)

    source_id: int | None = Field(
        default=None,
        foreign_key="sources.id",
        index=True,
    )

    category_id: int | None = Field(
        default=None,
        foreign_key="categories.id",
        index=True,
    )

    subcategory_id: int | None = Field(
        default=None,
        foreign_key="subcategories.id",
        index=True,
    )

    url: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    title: str = Field(max_length=500)

    author: str | None = Field(
        default=None,
        max_length=255,
    )

    image_url: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_correction: bool = Field(
        default=False,
        index=True,
    )

    published_at: datetime | None = Field(
        default=None,
        index=True,
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
    )


class ArticleSummary(SQLModel, table=True):
    __tablename__ = "article_summaries"

    id: int | None = Field(default=None, primary_key=True)
    article_id: int = Field(
        foreign_key="articles.id",
        index=True,
    )

    summary_type: str = Field(
        default="default",
        max_length=30,
    )

    summary_title: str = Field(max_length=500)

    summary_text: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    keywords: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )

    entities: dict | list | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )

    topic_processed_at: datetime | None = Field(
        default=None,
    )


class ArticleSimilarity(SQLModel, table=True):
    __tablename__ = "article_similarities"

    id: int | None = Field(default=None, primary_key=True)

    article_id: int = Field(
        foreign_key="articles.id",
        index=True,
    )

    related_article_id: int = Field(
        foreign_key="articles.id",
        index=True,
    )

    similarity_score: float