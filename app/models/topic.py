from datetime import datetime

from sqlmodel import Field, SQLModel


class Topic(SQLModel, table=True):
    __tablename__ = "topics"

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(
        unique=True,
        index=True,
        max_length=191,
    )

    note: str | None = Field(
        default=None,
        max_length=500,
    )


class ArticleTopic(SQLModel, table=True):
    __tablename__ = "article_topics"

    id: int | None = Field(default=None, primary_key=True)

    topic_id: int = Field(
        foreign_key="topics.id",
        index=True,
    )

    article_id: int = Field(
        foreign_key="articles.id",
        index=True,
    )

    summary_id: int | None = Field(
        default=None,
        foreign_key="article_summaries.id",
    )

    confidence: float = 1.0


class TopicMetric(SQLModel, table=True):
    __tablename__ = "topic_metrics"

    id: int | None = Field(default=None, primary_key=True)

    topic_id: int = Field(
        foreign_key="topics.id",
        index=True,
    )

    metric_type: str = Field(max_length=32)
    time_window: str | None = Field(default=None, max_length=16)

    score: float | None = None
    mention_count: int | None = None
    unique_sources: int | None = None

    calculated_at: datetime | None = None