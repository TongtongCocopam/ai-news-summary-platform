from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import AppException
from app.exceptions.error_code import ErrorCode
from app.models.article import ArticleSummary
from app.repositories.article_repository import ArticleRepository
from app.schemas.article import (
    ArticleDetailResponse,
    ArticleItemResponse,
    FactCheckResponse,
    RelatedArticleResponse,
)


class ArticleService:

    def __init__(self, session: AsyncSession):
        self.article_repository = ArticleRepository(session)

    @staticmethod
    def _group_summaries(
        summaries: list[ArticleSummary],
    ) -> dict[int, list[ArticleSummary]]:

        result = defaultdict(list)

        for summary in summaries:
            result[summary.article_id].append(summary)

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

        if default_summary:
            return default_summary

        bullet_summary = next(
            (
                summary
                for summary in summaries
                if summary.summary_type == "bullets"
            ),
            None,
        )

        return bullet_summary or summaries[0]

    async def search_articles(
        self,
        keyword: str,
        offset: int,
        limit: int,
    ) -> list[ArticleItemResponse]:

        article_ids = await self.article_repository.search_ids(
            keyword=keyword,
            offset=offset,
            limit=limit,
        )

        rows = await self.article_repository.find_articles_with_source(
            article_ids
        )

        summaries = await self.article_repository.find_summaries(
            article_ids
        )

        summary_map = self._group_summaries(summaries)

        article_map = {
            article.id: (article, source)
            for article, source in rows
        }

        result = []

        # 검색 결과 순서 유지
        for article_id in article_ids:
            article, source = article_map[article_id]

            summary = self._choose_summary(
                summary_map.get(article_id, [])
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
                    image_url=article.image_url,
                    outlet=source.name if source else None,
                    url=article.url,
                    published_at=article.published_at,
                )
            )

        return result

    async def get_article(
        self,
        article_id: int,
    ) -> ArticleDetailResponse:

        row = await self.article_repository.find_by_id(
            article_id
        )

        if row is None:
            raise AppException(
                ErrorCode.ARTICLE_NOT_FOUND
            )

        article, source = row

        summaries = await self.article_repository.find_summaries(
            [article_id]
        )

        summary = self._choose_summary(summaries)

        fact_check_rows = (
            await self.article_repository.find_fact_checks(
                article_id
            )
        )

        fact_checks = [
            FactCheckResponse(
                compared_article_id=compared_article.id,
                similarity_score=fact_check.similarity_score,
                check_result=fact_check.check_result,
                title=compared_article.title,
                outlet=(
                    compared_source.name
                    if compared_source
                    else None
                ),
            )
            for (
                fact_check,
                compared_article,
                compared_source,
            ) in fact_check_rows
        ]

        return ArticleDetailResponse(
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
            image_url=article.image_url,
            outlet=source.name if source else None,
            url=article.url,
            published_at=article.published_at,
            fact_checks=fact_checks,
        )

    async def get_related_articles(
        self,
        article_id: int,
        limit: int,
    ) -> list[RelatedArticleResponse]:

        # 원본 기사 존재 확인
        article = await self.article_repository.find_by_id(
            article_id
        )

        if article is None:
            raise AppException(
                ErrorCode.ARTICLE_NOT_FOUND
            )

        rows = await self.article_repository.find_related(
            article_id=article_id,
            limit=limit,
        )

        related_ids = [
            related_article.id
            for _, related_article, _ in rows
        ]

        summaries = await self.article_repository.find_summaries(
            related_ids
        )

        summary_map = self._group_summaries(summaries)

        result = []

        for similarity, article, source in rows:
            summary = self._choose_summary(
                summary_map.get(article.id, [])
            )

            result.append(
                RelatedArticleResponse(
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
                    image_url=article.image_url,
                    outlet=source.name if source else None,
                    url=article.url,
                    published_at=article.published_at,
                    similarity_score=similarity.similarity_score,
                )
            )

        return result

    async def get_corrections(
        self,
        since_hours: int,
        limit: int,
    ) -> list[ArticleItemResponse]:

        since = datetime.now() - timedelta(
            hours=since_hours
        )

        rows = await self.article_repository.find_corrections(
            since=since,
            limit=limit,
        )

        article_ids = [
            article.id
            for article, _ in rows
        ]

        summaries = await self.article_repository.find_summaries(
            article_ids
        )

        summary_map = self._group_summaries(summaries)

        result = []

        for article, source in rows:
            summary = self._choose_summary(
                summary_map.get(article.id, [])
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
                    image_url=article.image_url,
                    outlet=source.name if source else None,
                    url=article.url,
                    published_at=article.published_at,
                )
            )

        return result