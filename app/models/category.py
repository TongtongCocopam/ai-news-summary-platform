from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import UniqueConstraint


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)

    code: str = Field(
        unique=True,
        index=True,
        max_length=64,
    )

    name: str = Field(max_length=191)

    subcategories: list["Subcategory"] = Relationship(
        back_populates="category"
    )


class Subcategory(SQLModel, table=True):
    __tablename__ = "subcategories"

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "code",
            name="uq_subcategory_category_code",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    category_id: int = Field(
        foreign_key="categories.id",
        index=True,
    )

    code: str = Field(
        index=True,
        max_length=64,
    )

    name: str = Field(max_length=191)

    category: Category = Relationship(
        back_populates="subcategories"
    )