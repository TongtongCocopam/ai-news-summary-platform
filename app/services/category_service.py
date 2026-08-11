from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import AppException
from app.exceptions.error_code import ErrorCode
from app.models.article import ArticleSummary
from app.repositories.article_repository import ArticleRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.article import ArticleItemResponse
from app.schemas.category import (
    CategoryResponse,
    SubcategoryResponse,
)


class CategoryService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.category_repository = CategoryRepository(
            session
        )

        self.article_repository = ArticleRepository(
            session
        )

    async def get_categories(
        self,
    ) -> list[CategoryResponse]:

        categories = (
            await self.category_repository.find_all()
        )

        return [
            CategoryResponse(
                id=category.id,
                code=category.code,
                name=category.name,
                subcategories=[
                    SubcategoryResponse(
                        id=subcategory.id,
                        code=subcategory.code,
                        name=subcategory.name,
                    )
                    for subcategory
                    in category.subcategories
                ],
            )
            for category in categories
        ]

    async def get_articles(
        self,
        category_id: int,
        subcategory_id: int | None,
        offset: int,
        limit: int,
    ) -> list[ArticleItemResponse]:

        category = (
            await self.category_repository.find_by_id(
                category_id
            )
        )

        if category is None:
            raise AppException(
                ErrorCode.CATEGORY_NOT_FOUND
            )

        if subcategory_id is not None:
            subcategory = (
                await self.category_repository.find_subcategory(
                    category_id=category_id,
                    subcategory_id=subcategory_id,
                )
            )

            if subcategory is None:
                raise AppException(
                    ErrorCode.SUBCATEGORY_NOT_FOUND
                )

        article_ids = (
            await self.article_repository.find_ids_by_category(
                category_id=category_id,
                subcategory_id=subcategory_id,
                offset=offset,
                limit=limit,
            )
        )

        if not article_ids:
            return []

        article_rows = (
            await self.article_repository.find_articles_with_source(
                article_ids
            )
        )

        summaries = (
            await self.article_repository.find_summaries(
                article_ids
            )
        )

        summary_map: dict[
            int,
            list[ArticleSummary]
        ] = {}

        for summary in summaries:
            summary_map.setdefault(
                summary.article_id,
                [],
            ).append(summary)

        article_map = {
            article.id: (article, source)
            for article, source in article_rows
        }

        result = []

        for article_id in article_ids:
            article, source = article_map[
                article_id
            ]

            summary = self._choose_summary(
                summary_map.get(
                    article_id,
                    [],
                )
            )

            result.append(
                ArticleItemResponse(
                    id=article.id,
                    title=(
                        summary.summary_title
                        if summary
                        else article.title
                    ),
                    original_title=article.title,
                    summary=(
                        summary.summary_text
                        if summary
                        else None
                    ),
                    author=article.author,
                    # image_url=article.image_url,
                    outlet=(
                        source.name
                        if source
                        else None
                    ),
                    url=article.url,
                    published_at=article.published_at,
                )
            )

        return result

    @staticmethod
    def _choose_summary(
        summaries: list[ArticleSummary],
    ) -> ArticleSummary | None:

        if not summaries:
            return None

        default_summary = next(
            (
                summary
                for summary in summaries
                if summary.summary_type == "default"
            ),
            None,
        )

        return default_summary or summaries[0]