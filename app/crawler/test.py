import asyncio

from app.crawler.naver_news import NaverNewsCrawler


async def main():
    crawler = NaverNewsCrawler()

    articles = await crawler.crawl(
        "20260811",
        limit=20,
    )

    print(
        f"수집 결과: {len(articles)}개"
    )

    for article in articles[:3]:
        print(article)


if __name__ == "__main__":
    asyncio.run(main())
