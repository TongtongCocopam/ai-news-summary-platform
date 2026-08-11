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

    async def find_by_codes(
            self,
            codes: set[str],
    ) -> list[Category]:

        if not codes:
            return []

        statement = (
            select(Category)
            .where(
                col(Category.code).in_(codes)
            )
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def find_subcategories(
            self,
            category_ids: set[int],
            codes: set[str],
    ) -> list[Subcategory]:

        if not category_ids or not codes:
            return []

        statement = (
            select(Subcategory)
            .where(
                col(Subcategory.category_id).in_(
                    category_ids
                ),
                col(Subcategory.code).in_(
                    codes
                ),
            )
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    def add_categories(
            self,
            categories: list[Category],
    ) -> None:
        self.session.add_all(categories)

    def add_subcategories(
            self,
            subcategories: list[Subcategory],
    ) -> None:
        self.session.add_all(subcategories)