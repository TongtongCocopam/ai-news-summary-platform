import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Index,
    UniqueConstraint,
    text,
)
from sqlmodel import Field, SQLModel


class CheckResultEnum(str, enum.Enum):
    RELIABILITY_VERY_HIGH = "reliability_very_high"
    RELIABILITY_HIGH = "reliability_high"
    RELIABILITY_LOW = "reliability_low"
    CROSS_CHECK_REQUIRED = "cross_check_required"


class FactCheckResult(SQLModel, table=True):
    __tablename__ = "fact_check_results"

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "compared_article_id",
            name="uq_fact_check_article_pair",
        ),
        Index(
            "idx_fact_check_compared_article_id",
            "compared_article_id",
        ),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    article_id: int = Field(
        foreign_key="articles.id",
    )

    compared_article_id: int = Field(
        foreign_key="articles.id",
    )

    similarity_score: float

    check_result: CheckResultEnum = Field(
        sa_column=Column(
            SAEnum(
                CheckResultEnum,
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
                name="check_result_enum",
            ),
            nullable=False,
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )
    )