from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import (
    Topic,
    ArticleTopic,
    TopicMetric,
)
from app.repositories.topic_processing_repository import (
    TopicProcessingRepository,
)


class TopicProcessingService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TopicProcessingRepository(session)

    async def process_summaries(
        self,
        limit: int = 500,
    ) -> int:

        async with self.session.begin():

            summaries = (
                await self.repository.find_unprocessed_summaries(
                    limit
                )
            )

            if not summaries:
                return 0

            keyword_names = {
                keyword.strip()
                for summary in summaries
                for keyword in (summary.keywords or [])
                if keyword and keyword.strip()
            }

            existing_topics = (
                await self.repository.find_topics_by_names(
                    keyword_names
                )
            )

            topic_map = {
                topic.name: topic
                for topic in existing_topics
            }

            new_topics = [
                Topic(name=name)
                for name in keyword_names
                if name not in topic_map
            ]

            if new_topics:
                self.repository.add_all(new_topics)

                # INSERT 실행해서 id 확보
                await self.session.flush()

                for topic in new_topics:
                    topic_map[topic.name] = topic

            article_ids = {
                summary.article_id
                for summary in summaries
            }

            existing_pairs = (
                await self.repository.find_existing_assignments(
                    article_ids
                )
            )

            new_pairs = set()
            assignments = []

            for summary in summaries:

                keywords = {
                    keyword.strip()
                    for keyword in (summary.keywords or [])
                    if keyword and keyword.strip()
                }

                for keyword in keywords:
                    topic = topic_map[keyword]

                    pair = (
                        topic.id,
                        summary.article_id,
                    )

                    if (
                        pair in existing_pairs
                        or pair in new_pairs
                    ):
                        continue

                    assignments.append(
                        ArticleTopic(
                            topic_id=topic.id,
                            article_id=summary.article_id,
                            summary_id=summary.id,
                        )
                    )

                    new_pairs.add(pair)

                # keyword가 없어도 처리 자체는 완료
                summary.topic_processed_at = datetime.now()

            if assignments:
                self.repository.add_all(assignments)

        return len(summaries)