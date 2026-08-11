from sqlalchemy.ext.asyncio import AsyncSession

from app.crawler.naver_news import (
    CrawledArticle,
    NaverNewsCrawler,
)
from app.models.article import Article
from app.models.category import (
    Category,
    Subcategory,
)
from app.models.source import Source
from app.repositories.article_repository import (
    ArticleRepository,
)
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.repositories.source_repository import (
    SourceRepository,
)


class NewsCrawlService:
    def __init__(
        self,
        session: AsyncSession,
        crawler: NaverNewsCrawler,
    ):
        self.session = session
        self.crawler = crawler

        self.article_repository = (
            ArticleRepository(session)
        )

        self.category_repository = (
            CategoryRepository(session)
        )

        self.source_repository = (
            SourceRepository(session)
        )

    async def crawl_and_save(
        self,
        target_date: str,
        crawl_limit: int | None = None,
        batch_size: int = 200,
    ) -> int:
        """
        크롤링 + batch 저장 전체

        :param target_date: 타겟 날짜
        :param crawl_limit: 크롤링 갯수 제한
        :param batch_size: 한번에 저장할 데이터
        :return: 저장한 기사 개수
        """

        crawled_articles = (
            await self.crawler.crawl(
                target_date=target_date,
                limit=crawl_limit,
            )
        )
        print("=== 크롤링 결과 ===")

        for article in crawled_articles:
            print(article)
        print(
            f"상세 파싱 완료: "
            f"{len(crawled_articles)}개"
        )

        saved_count = 0

        for start in range(
            0,
            len(crawled_articles),
            batch_size,
        ):
            batch = crawled_articles[
                start:start + batch_size
            ]

            saved_count += (
                await self._save_batch(batch)
            )

        return saved_count


    async def _save_batch(
        self,
        items: list[CrawledArticle],
    ) -> int:
        """
            크롤링된 기사를 일정 단위로 DB에 저장

            이미 존재하는 URL은 제외하고,
            필요한 Category/Subcategory/Source를 준비한 후
            신규 Article만 저장

            이 메서드 단위로 하나의 트랜잭션을 사용
            """
        if not items:
            return 0

        async with self.session.begin():

            urls = {
                item.url
                for item in items
            }

            existing_urls = (
                await self.article_repository
                .find_existing_urls(urls)
            )

            new_items = [
                item
                for item in items
                if item.url
                not in existing_urls
            ]

            if not new_items:
                return 0

            category_map = (
                await self._prepare_categories(
                    new_items
                )
            )

            subcategory_map = (
                await self._prepare_subcategories(
                    new_items,
                    category_map,
                )
            )

            source_map = (
                await self._prepare_sources(
                    new_items
                )
            )

            articles: list[Article] = []

            for item in new_items:
                category = category_map[
                    item.category_code
                ]

                subcategory = subcategory_map[
                    (
                        category.id,
                        item.subcategory_code,
                    )
                ]

                # 언론사 파싱이 안 된 기사는
                # 현재는 저장하지 않음
                if not item.outlet:
                    continue

                source = source_map.get(
                    item.outlet
                )

                if source is None:
                    continue

                articles.append(
                    Article(
                        source_id=source.id,
                        category_id=category.id,
                        subcategory_id=subcategory.id,
                        url=item.url,
                        title=item.title,
                        content=item.content,
                        author=item.author,
                        # image_url=item.image_url,

                        is_correction=(
                            item.is_correction
                        ),

                        published_at=(
                            item.published_at
                        ),
                    )
                )

            self.article_repository.add_all(
                articles
            )

            return len(articles)


    async def _prepare_categories(
        self,
        items: list[CrawledArticle],
    ) -> dict[str, Category]:

        names_by_code = {
            item.category_code:
                item.category_name
            for item in items
        }

        codes = set(
            names_by_code.keys()
        )

        existing = (
            await self.category_repository
            .find_by_codes(codes)
        )

        category_map = {
            category.code: category
            for category in existing
        }

        missing = [
            Category(
                code=code,
                name=name,
            )
            for code, name
            in names_by_code.items()
            if code not in category_map
        ]

        if missing:
            self.category_repository.add_categories(
                missing
            )

            # 새 Category의 id 받아오기
            await self.session.flush()

            for category in missing:
                category_map[
                    category.code
                ] = category

        return category_map


    async def _prepare_subcategories(
        self,
        items: list[CrawledArticle],
        category_map: dict[str, Category],
    ) -> dict[
        tuple[int, str],
        Subcategory,
    ]:

        required: dict[
            tuple[int, str],
            str,
        ] = {}

        for item in items:
            category = category_map[
                item.category_code
            ]

            required[
                (
                    category.id,
                    item.subcategory_code,
                )
            ] = item.subcategory_name

        category_ids = {
            category_id
            for category_id, _
            in required.keys()
        }

        codes = {
            code
            for _, code
            in required.keys()
        }

        existing = (
            await self.category_repository
            .find_subcategories(
                category_ids=category_ids,
                codes=codes,
            )
        )

        subcategory_map = {
            (
                subcategory.category_id,
                subcategory.code,
            ): subcategory
            for subcategory in existing
        }

        missing: list[Subcategory] = []

        for (
            category_id,
            code,
        ), name in required.items():

            key = (
                category_id,
                code,
            )

            if key in subcategory_map:
                continue

            missing.append(
                Subcategory(
                    category_id=category_id,
                    code=code,
                    name=name,
                )
            )

        if missing:
            self.category_repository\
                .add_subcategories(
                    missing
                )

            await self.session.flush()

            for subcategory in missing:
                subcategory_map[
                    (
                        subcategory.category_id,
                        subcategory.code,
                    )
                ] = subcategory

        return subcategory_map


    async def _prepare_sources(
        self,
        items: list[CrawledArticle],
    ) -> dict[str, Source]:

        names = {
            item.outlet
            for item in items
            if item.outlet
        }

        existing = (
            await self.source_repository
            .find_by_names(names)
        )

        source_map = {
            source.name: source
            for source in existing
        }

        missing = [
            Source(
                name=name
            )
            for name in names
            if name not in source_map
        ]

        if missing:
            self.source_repository.add_all(
                missing
            )

            await self.session.flush()

            for source in missing:
                source_map[
                    source.name
                ] = source

        return source_map