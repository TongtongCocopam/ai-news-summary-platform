from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from app.models.category import Category, Subcategory


class CategoryRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(
        self,
    ) -> list[Category]:

        statement = (
            select(Category)
            .options(
                selectinload(Category.subcategories)
            )
            .order_by(
                col(Category.id)
            )
        )

        result = await self.session.execute(statement)

        return list(
            result.scalars().all()
        )

    async def find_by_id(
        self,
        category_id: int,
    ) -> Category | None:

        statement = (
            select(Category)
            .where(
                col(Category.id) == category_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def find_subcategory(
        self,
        category_id: int,
        subcategory_id: int,
    ) -> Subcategory | None:

        statement = (
            select(Subcategory)
            .where(
                col(Subcategory.id) == subcategory_id,
                col(Subcategory.category_id) == category_id,
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()