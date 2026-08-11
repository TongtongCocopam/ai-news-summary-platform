# SumNews

뉴스 기사를 수집하고 카테고리·이슈·트렌드 정보를 제공하는  
FastAPI 기반 뉴스 백엔드 프로젝트입니다.

기존 대학 프로젝트에서 작성했던 크롤링 및 뉴스 처리 로직을  
백엔드 구조와 유지보수성을 중심으로 재설계하고 있습니다.

## 주요 기능

### 구현 완료

- 회원가입 / 로그인
- JWT 기반 인증
- 네이버 뉴스 기사 수집
- 카테고리 / 서브카테고리 분류
- 기사 상세 정보 수집
  - 제목
  - 본문
  - 언론사
  - 기자
  - 발행일
- URL 기반 중복 기사 방지
- 비동기 기사 상세 크롤링
- 기사 데이터 DB 저장
- 카테고리별 기사 조회
- 기사 상세 조회
- 트렌드 / 이슈 조회 API

### 개발 예정

- 기사 요약
- 핵심 키워드 추출
- Topic 생성 및 기사 연결
- 일별 Topic 통계 집계
- 주요 이슈 생성
- 관련 기사 추천

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLModel
- SQLAlchemy Async
- Pydantic

### Database

- MySQL
- Alembic

### Crawling

- Selenium
- BeautifulSoup
- HTTPX
- asyncio

### Infrastructure

- Docker

---

## Architecture

```text
app/
├── router/          # API Endpoint
├── services/        # Business Logic
├── repositories/    # Data Access
├── models/          # Database Model
├── schemas/         # Request / Response DTO
├── dependencies/    # FastAPI Dependency
├── crawler/         # News Crawling
├── jobs/            # Batch Job
├── db/              # Database Session
├── core/            # Application Config
└── exceptions/      # Exception Handling
```

Router → Service → Repository 구조를 사용하여  
API 계층, 비즈니스 로직, 데이터 접근 로직을 분리했습니다.

---

## News Crawling

뉴스 크롤링은 URL 수집과 기사 상세 수집을 분리했습니다.

```text
Naver News
    │
    ▼
Selenium
기사 URL 수집
    │
    ▼
URL 중복 제거
    │
    ▼
HTTPX AsyncClient
기사 상세 페이지 비동기 요청
    │
    ▼
BeautifulSoup
기사 데이터 파싱
    │
    ▼
Service
    │
    ▼
MySQL
```
## Selenium

네이버 뉴스 목록은 동적 콘텐츠를 포함하므로
Selenium을 이용해 기사 목록을 로딩하고 URL을 수집합니다.

Selenium은 동기 API이기 때문에
`asyncio.to_thread()`를 이용하여 별도 Thread에서 실행합니다.

## Async Crawling

기사 상세 페이지는 HTTPX의 AsyncClient를 이용하여
비동기로 요청합니다.

```
semaphore = asyncio.Semaphore(10)
```

Semaphore를 사용하여 네이버 서버로 전달되는
동시 HTTP 요청 수를 제한합니다.

## Batch Save

크롤링이 완료된 기사 데이터는 일정 크기의 Batch로 나누어
DB Transaction을 수행합니다.

이를 통해 많은 데이터를 한 번에 처리할 때 발생할 수 있는
Transaction 크기와 메모리 사용량을 제한합니다.

---
## Database Migration
```
uv run alembic revision --autogenerate -m "migration message"
uv run alembic upgrade head
```

## Run
```
uv run uvicorn app.main:app --reload
```

뉴스 크롤링 Job:
```
uv run python -m app.jobs.crawl_news
```
---
## Environment Variables

`.env`
```
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_HOST=
MYSQL_PORT=
MYSQL_DATABASE=

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Refactoring

본 프로젝트는 기존 대학 프로젝트를 기반으로
다음 부분을 중점적으로 개선하고 있습니다.

- 크롤러와 DB 접근 로직 분리
- Service / Repository 계층 분리
- 동기 기사 수집을 비동기 처리로 개선
- DB Transaction 책임을 Service 계층으로 이동
- Alembic 기반 Schema Migration 관리
- 환경변수 기반 설정 관리
- API 응답 및 예외 처리 구조 통일