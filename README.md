# AI 기반 뉴스 요약 및 개인화 브리핑 서비스

AI를 활용하여 뉴스 범람 시대의 정보 과부하를 해결하고, 
사용자 맞춤형 다각 시선 비교 및 RAG 기반 질의응답을 제공하는 프로젝트입니다.

## Tech Stack
- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: React
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy
- **AI**: GPT-4o, LangChain (RAG)
- **Deployment**: Docker (제외 가능)

## Key Features
- **Contextual Summarization**: 여러 기사를 통합하여 사건의 타임라인별 요약 제공
- ~~**Perspective Analysis**: 동일 이슈에 대한 언론사별 관점(보수/진보/중립) 비교~~
- **News RAG**: 기사 본문에 근거한 실시간 대화형 질의응답
- **Personalization**: 사용자 관심 카테고리 기반 추천 및 북마크 히스토리 관리

## Database Schema
- API 리소스 중심의 설계 (`articles`, `users`, `trends`, `topics` 등)
- **본문 데이터(content) 보관**: 정확한 AI 요약 및 RAG 성능 확보를 위한 설계 반영

## Quick Start
1. 라이브러리 설치
   ```bash
   pip install -r requirements.txt
   
2. .env.example참고
    db비밀번호, 이름, 링크 등 변수 넣어야 함

3. 서버 실행
uvicorn main:app --reload