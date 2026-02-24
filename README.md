[README.md](https://github.com/user-attachments/files/23831982/README.md)
# Newsbot Backend (Capstone 25-2)

FastAPI + MySQL 기반 뉴스 요약/추천/팩트체크 API 서버 🚀  
(DB 담당자: [이경빈])

---

## ⚙️ 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
2. 환경 변수 설정
프로젝트 루트에 .env 파일을 만들어 아래 내용을 넣어주세요.
⚠️ .env는 깃허브에 올리면 안 됩니다!

ini
코드 복사
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=비밀번호
MYSQL_DB=newsbot_mvp

API_TOKEN=팀공유토큰
3. 서버 실행
bash
코드 복사
uvicorn backend.main:app --reload
서버가 실행되면 Swagger 문서에서 API 테스트 가능:
👉 http://127.0.0.1:8000/docs

🔑 인증
모든 API 요청에는 헤더에 토큰이 필요합니다.

css
코드 복사
x-api-token: {API_TOKEN}
Swagger에서 Authorize 버튼 클릭 후 토큰 입력 → 자동 적용됩니다.

📚 주요 엔드포인트
Ingest (데이터 입력)
POST /ingest/source → 출처 등록 (name, domain)

POST /articles/upsert-by-url → URL 기준 기사 업서트

POST /ingest/summary → 기사 요약 저장

POST /topic/assign → 토픽 할당

조회/분석
GET /articles/search → 기사 검색

GET /topics/hot → 핫토픽 조회 (1h, 24h, 7d, 30d)

POST /topics/refresh-hotness → 핫토픽 점수 갱신

POST /similarity/batch-upsert → 기사 유사도 관계 저장

GET /articles/{id}/recommendations → 유사 기사 추천

POST /factcheck → 팩트체크 결과 저장

GET /articles/{id}/factcheck → 팩트체크 조회

관리/운영
GET /health → 서버 및 DB 상태 체크 (토큰 불필요)

🧪 Postman 컬렉션
Postman 컬렉션(JSON)을 제공합니다.
👉 docs/newsbot.postman_collection.json 파일을 Import 후,
baseUrl / apiToken 변수만 세팅하면 바로 테스트 가능합니다.

📌 주의사항
.env 절대 깃허브에 업로드하지 마세요.

DB 마이그레이션은 schema.sql 파일 참고.

테스트 데이터는 DB에 미리 일부 들어가 있으니 바로 호출 가능.

👥 역할 분담
크롤러 팀: 기사 수집 후 /articles/upsert-by-url 호출

LLM 요약 팀: /ingest/summary, /topic/assign 호출

분석 팀: /similarity/batch-upsert, /factcheck 호출

프론트/서비스 팀: /topics/hot, /articles/{id}/recommendations, /articles/{id}/factcheck 조회

DB 스키마 링크
https://dbdiagram.io/d/68cfe08d960f6d821a1476da

DB 1차 수정내역
1️⃣ source
컬럼	타입	설명
id	INT	PK
name	VARCHAR(191)	언론사 이름 (예: “연합뉴스”)
domain	VARCHAR(191)	언론사 도메인 (예: “yna.co.kr”)

📝 기자 정보는 여기 들어가지 않음. “언론사 단위” 테이블임.

2️⃣ category / subcategory
테이블	역할
category	대분류(예: IT/과학, 사회, 경제 등)
subcategory	소분류(예: 모바일, 증시, 사건사고 등)

둘은 1:N 관계.
subcategory.category_id가 FK로 연결되어 있어요.
API에서는 subcategory_code만 넣어도 자동으로 category_id가 세팅됩니다.

3️⃣ article
컬럼	타입	설명
id	INT	PK
source_id	INT	언론사(FK → source)
category_id	INT	대분류
subcategory_id	INT	소분류
url	VARCHAR(1000)	기사 원문 URL (Unique)
title	VARCHAR(500)	기사 제목
author	VARCHAR(255)	기자 이름 (새로 추가)
image_url	VARCHAR(1000)	대표 이미지 URL (새로 추가)
published_at	DATETIME	기사 작성/게시일
created_at	DATETIME	DB 등록 시각
4️⃣ summary
컬럼	타입	설명
id	INT	PK
article_id	INT	기사 FK
summary_type	VARCHAR(32)	요약 종류 (“headline”, “bullets”, “brief”)
summary_text	TEXT	요약문 내용
keywords	JSON	핵심 키워드 배열
entities	JSON	개체명 배열![img.png](img.png)
created_at	DATETIME	생성 시각
5️⃣ topic / topic_assignment / topic_metrics

topic: 토픽(이슈 키워드 단위)

topic_assignment: 기사에 어떤 토픽이 붙었는지 (confidence 포함)

topic_metrics: 토픽의 hotness 점수, 시계열 통계

6️⃣ article_similarity

기사 간 유사도 저장.

(article_id, related_article_id) 한 쌍당 하나씩.

7️⃣ fact_check_result

기사 간 진위/대조 결과.

(article_id, compared_article_id) 한 쌍당 하나씩.

check_result 값: "similar", "conflict", "unverified" 중 하나.
