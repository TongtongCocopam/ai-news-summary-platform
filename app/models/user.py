from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
    )

    password_hash: str = Field(
        max_length=255,
    )

    nickname: str = Field(
        max_length=50,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

# 나중에 업데이트 시 시간 변경 되도록 바꿀 것
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
