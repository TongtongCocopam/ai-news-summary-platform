import asyncio
from datetime import datetime

from app.crawler.naver_news import (
    NaverNewsCrawler,
)
from app.db.session import AsyncSessionLocal
from app.services.news_crawl_service import (
    NewsCrawlService,
)


async def main():
    crawler = NaverNewsCrawler(
        concurrency=10
    )

    async with AsyncSessionLocal() as session:
        service = NewsCrawlService(
            session=session,
            crawler=crawler,
        )

        target_date = datetime.now().strftime(
            "%Y%m%d"
        )

        saved = await service.crawl_and_save(
            target_date=target_date,
            batch_size=100,
        )

        print(
            f"DB 저장 완료: {saved}개"
        )


if __name__ == "__main__":
    asyncio.run(main())