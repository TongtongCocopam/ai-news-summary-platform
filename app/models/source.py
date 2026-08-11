from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(
        index=True,
        max_length=191,
    )

    domain: str | None = Field(
        default=None,
        max_length=191,
    )
