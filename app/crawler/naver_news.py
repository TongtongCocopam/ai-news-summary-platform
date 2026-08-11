import re
import asyncio
import hashlib
from datetime import datetime
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

CORRECTION_KEYWORDS = (
    "정정 보도",
    "정정보도",
    "반론 보도",
    "반론보도",
    "추후보도",
    "추후 보도",
    "바로잡습니다",
)


@dataclass(frozen=True)
class NewsSection:
    """크롤링 대상 뉴스 카테고리/서브카테고리 설정"""
    category_code: str
    category_name: str

    subcategory_code: str
    subcategory_name: str

    url: str


@dataclass
class ArticleUrl:
    """뉴스 목록 페이지에서 수집한 기사 URL과 분류 정보"""
    url: str

    category_code: str
    category_name: str

    subcategory_code: str
    subcategory_name: str


@dataclass
class CrawledArticle:
    url: str
    category_code: str
    category_name: str
    subcategory_code: str
    subcategory_name: str
    title: str
    content: str
    outlet: str | None
    author: str | None
    # image_url: str | None
    published_at: datetime
    is_correction: bool


def slug(value: str) -> str:
    """문자열을 DB code로 사용할 수 있는 형식으로 정규화"""
    raw = (value or "").strip()

    value = re.sub(
        r"[\s_]+",
        "-",
        raw,
    )

    value = re.sub(
        r"[^0-9A-Za-z\-가-힣]",
        "",
        value,
    )

    value = value.lower().strip("-")

    if value:
        return value[:64]

    digest = hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()[:10]

    return f"code-{digest}"


def parse_datetime(
        value: str,
) -> datetime | None:
    """기사 발행 시각 문자열을 datetime으로 변환"""
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S",
        )

    except ValueError:
        try:
            return datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            ).replace(
                tzinfo=None
            )

        except ValueError:
            return None


class NaverNewsCrawler:
    """
    네이버 뉴스의 기사 URL을 수집하고,
    기사 상세 페이지를 비동기로 요청하여 필요한 데이터를 파싱.

    Selenium:
        서브카테고리 페이지의 동적 콘텐츠 및 기사 URL 수집

    httpx:
        수집된 기사 상세 페이지를 비동기로 요청

    concurrency:
        동시에 요청할 수 있는 기사 상세 페이지 수
    """
    NEWS_SECTIONS = (
        NewsSection(
            category_code="economy",
            category_name="경제",
            subcategory_code="finance",
            subcategory_name="금융",
            url="https://news.naver.com/breakingnews/section/101/259",
        ),
        NewsSection(
            category_code="economy",
            category_name="경제",
            subcategory_code="stock",
            subcategory_name="증권",
            url="https://news.naver.com/breakingnews/section/101/258",
        ),
        NewsSection(
            category_code="economy",
            category_name="경제",
            subcategory_code="realestate",
            subcategory_name="부동산",
            url="https://news.naver.com/breakingnews/section/101/260",
        ),

        NewsSection(
            category_code="society",
            category_name="사회",
            subcategory_code="incident",
            subcategory_name="사건사고",
            url="https://news.naver.com/breakingnews/section/102/249",
        ),
    )

    def __init__(
            self,
            concurrency: int = 10,
    ):
        # 기사 상세 페이지의 최대 동시 요청 수
        self.concurrency = concurrency
        # 네이버 뉴스 HTTP 요청에 사용할 공통 Header
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9",
        }

    @staticmethod
    def _create_driver() -> WebDriver:
        """기사 목록 수집에 사용할 Selenium Chrome Driver 생성"""
        options = webdriver.ChromeOptions()
        # 크롤링에 필요 없는 Chrome 기능 비활성화
        options.add_argument(
            "--no-sandbox"
        )
        options.add_argument(
            "--disable-dev-shm-usage"
        )
        options.add_argument(
            "--disable-extensions"
        )
        options.add_argument(
            "--disable-notifications"
        )
        # 화면을 띄우지 않고 Headless 모드로 실행
        options.add_argument("--headless=new")
        # 기사 목록 수집에는 이미지가 필요 없으므로 로딩 차단
        prefs = {
            "profile.managed_default_content_settings.images": 2
        }

        options.add_experimental_option(
            "prefs",
            prefs,
        )
        # 모든 리소스가 아닌 DOM 로딩까지만 기다림
        options.page_load_strategy = "eager"

        driver = webdriver.Chrome(
            options=options
        )
        # 페이지 로딩 최대 대기시간
        driver.set_page_load_timeout(20)

        return driver

    def _collect_urls_sync(
            self,
            target_date: str,
    ) -> list[ArticleUrl]:
        """
        모든 세부 카테고리에서 URL 수집
        - 하나의 Selenium Driver를 재사용
        - URL 기준 중복 제거
        - 작업 종료 시 Driver 해제
        :param target_date: 크롤링할 날짜
        :return: 기사 url
        """

        driver = self._create_driver()

        try:
            results: list[ArticleUrl] = []

            for section in self.NEWS_SECTIONS:
                try:
                    urls = self._crawl_section_sync(
                        driver=driver,
                        section=section,
                        target_date=target_date,
                    )
                    # 기사 목록을 하나의 리스트로 합치기
                    results.extend(urls)

                except Exception as error:
                    print(
                        f"[{section.category_name}/"
                        f"{section.subcategory_name}] "
                        f"수집 실패: {error}"
                    )
            # URL 중복 제거
            unique: dict[str, ArticleUrl] = {}

            for item in results:
                unique.setdefault(
                    item.url,
                    item,
                )

            return list(unique.values())
        # 무조건 Chrome 종료
        finally:
            driver.quit()

    def _crawl_section_sync(
            self,
            driver: WebDriver,
            section: NewsSection,
            target_date: str,
    ) -> list[ArticleUrl]:
        """
        특정 세부 카테고리 하나 크롤링
        :param driver: 드라이버
        :param section: 카테고리
        :param target_date: 날짜
        :return: 기사 url
        """
        print(
            f"[{section.category_name}/"
            f"{section.subcategory_name}] 크롤링 시작"
        )

        driver.get(
            f"{section.url}?date={target_date}"
        )
        # 대상 날짜의 기사가 모두 나올 때까지
        # '더보기' 버튼을 반복 클릭
        while True:
            try:
                button = WebDriverWait(
                    driver,
                    1,
                ).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            ".section_more_inner",
                        )
                    )
                )

                button.click()

            except Exception:
                break

        # 기사 링크 요소 찾기
        news_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "a.sa_text_title",
        )

        print(
            f"[{section.category_name}/"
            f"{section.subcategory_name}] "
            f"{len(news_elements)}개 발견"
        )

        results = []

        for element in news_elements:
            url = element.get_attribute("href")

            if not url:
                continue

            results.append(
                ArticleUrl(
                    url=url,
                    category_code=section.category_code,
                    category_name=section.category_name,
                    subcategory_code=section.subcategory_code,
                    subcategory_name=section.subcategory_name,
                )
            )

        return results

    async def collect_urls(
            self,
            target_date: str,
    ) -> list[ArticleUrl]:

        # Selenium은 동기 API이므로 이벤트 루프를 막지 않도록
        # 별도의 Thread에서 URL 수집 작업을 실행
        return await asyncio.to_thread(
            self._collect_urls_sync,
            target_date,
        )

    async def _parse_article(
            self,
            client: httpx.AsyncClient,
            item: ArticleUrl,
            semaphore: asyncio.Semaphore,
    ) -> CrawledArticle | None:
        """
        기사 상세 페이지 httpx 요청 + BeautifulSoup 파싱

        :param client: httpx
        :param item: 기사 url
        :param semaphore: 세마포어
        :return:파싱한 기사 데이터
        """
        try:
            async with semaphore:
                try:
                    response = await client.get(
                        item.url
                    )

                    response.raise_for_status()

                except httpx.HTTPError as error:
                    print(
                        f"기사 요청 실패: "
                        f"{item.url} / {error}"
                    )

                    return None

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            title_node = soup.select_one(
                ".media_end_head_headline"
            )

            body_node = soup.select_one(
                "#dic_area"
            )

            if title_node is None or body_node is None:
                return None

            title = title_node.get_text(
                " ",
                strip=True,
            )

            content = body_node.get_text(
                " ",
                strip=True,
            )

            if not title or not content:
                return None

            press_node = soup.select_one(
                ".media_end_head_top_press"
            )

            outlet = (
                press_node.get_text(strip=True)
                if press_node
                else None
            )

            author_node = soup.select_one(
                ".media_end_head_journalist_name"
            )

            author = (
                author_node.get_text(
                    strip=True
                )
                if author_node
                else None
            )

            date_node = soup.select_one(
                ".media_end_head_info_datestamp_time."
                "_ARTICLE_DATE_TIME"
            )

            date_value = (
                date_node.get(
                    "data-date-time",
                    "",
                )
                if date_node
                else ""
            )

            published_at = parse_datetime(
                date_value
            )

            if published_at is None:
                return None

            # image_node = soup.select_one(
            #     'meta[property="og:image"]'
            # )
            #
            # image_url = (
            #     image_node.get("content")
            #     if image_node
            #     else None
            # )

            is_correction = any(
                keyword in title
                for keyword in CORRECTION_KEYWORDS
            )

            return CrawledArticle(
                url=item.url,

                category_code=item.category_code,
                category_name=item.category_name,

                subcategory_code=item.subcategory_code,
                subcategory_name=item.subcategory_name,

                title=title,
                content=content,

                outlet=outlet,
                author=author,

                # image_url=image_url,

                published_at=published_at,

                is_correction=is_correction,
            )

        except httpx.HTTPError as error:
            print(
                f"기사 요청 실패: {item.url} / {error}"
            )
            return None

        except Exception as error:
            print(
                f"기사 파싱 실패: {item.url} / {error}"
            )
            return None

    async def crawl(
            self,
            target_date: str,
            limit: int | None = None,
    ) -> list[CrawledArticle]:
        """
        지정 날짜의 기사 URL을 수집한 후
        상세 페이지를 비동기로 파싱

        Args:
            target_date: 크롤링 대상 날짜. YYYYMMDD 형식

            limit:실제 상세 파싱할 최대 기사 수
                  None이면 수집된 기사 전체를 처리

        Returns: 대상 날짜와 일치하는 CrawledArticle 목록
        """

        urls = await self.collect_urls(
            target_date
        )

        print(
            f"기사 URL {len(urls)}개 수집"
        )

        if limit is not None:
            urls = urls[:limit]

        # 모든 기사 요청 Task생성, 실제 동시 HTTP 요청 수는 concurrency 값으로 제한
        semaphore = asyncio.Semaphore(
            self.concurrency
        )

        async with httpx.AsyncClient(
                headers=self.headers,
                timeout=15.0,
                follow_redirects=True,
        ) as client:
            tasks = [
                self._parse_article(
                    client=client,
                    item=item,
                    semaphore=semaphore,
                )
                for item in urls
            ]

            results = await asyncio.gather(
                *tasks
            )

        target = datetime.strptime(
            target_date,
            "%Y%m%d",
        ).date()

        return [
            article
            for article in results
            if article is not None
               and article.published_at.date() == target
        ]
