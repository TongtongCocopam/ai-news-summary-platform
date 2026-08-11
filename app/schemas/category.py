from sqlmodel import SQLModel

from app.schemas.article import ArticleItemResponse


class SubcategoryResponse(SQLModel):
    id: int
    code: str
    name: str


class CategoryResponse(SQLModel):
    id: int
    code: str
    name: str
    subcategories: list[SubcategoryResponse]