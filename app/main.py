from fastapi import FastAPI

from app.api import auth, users
from app.core.cors import setup_cors
from app.exceptions.handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI()

    setup_cors(app)
    register_exception_handlers(app)

    app.include_router(auth.router)
    app.include_router(users.router)

    return app


app = create_app()