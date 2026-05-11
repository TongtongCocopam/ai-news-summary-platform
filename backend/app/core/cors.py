from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from backend.app.core.config import settings

def setup_cors(app: FastAPI) -> None:
    # 환경변수에서 쉼표로 구분된 문자열을 리스트로 변환
    if isinstance(settings.CORS_ORIGINS, str):
        origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',')]
    else:
        origins = settings.CORS_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )