import asyncio
from datetime import date

from app.db.session import AsyncSessionLocal
from app.services.topic_processing_service import (
    TopicProcessingService,
)


async def main():

    async with AsyncSessionLocal() as session:
        service = TopicProcessingService(session)

        while True:
            processed = await service.process_summaries(
                limit=500
            )

            if processed == 0:
                break

            print(
                f"Summary {processed}개 토픽 처리 완료"
            )

        count = await service.compute_for_day(
            date.today()
        )

        print(
            f"TopicMetric {count}개 계산 완료"
        )


if __name__ == "__main__":
    asyncio.run(main())