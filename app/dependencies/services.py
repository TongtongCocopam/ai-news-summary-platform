from typing import Annotated
from fastapi import Depends

from app.db.session import SessionDep
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.trend_service import TrendService
from app.services.issue_service import IssueService
from app.services.article_service import ArticleService


def get_auth_service(
    session: SessionDep,
) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]

def get_user_service(
    session: SessionDep,
) -> UserService:
    return UserService(session)


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]

def get_trend_service(
    session: SessionDep,
) -> TrendService:
    return TrendService(session)


TrendServiceDep = Annotated[
    TrendService,
    Depends(get_trend_service),
]

def get_issue_service(
    session: SessionDep,
) -> IssueService:
    return IssueService(session)


IssueServiceDep = Annotated[
    IssueService,
    Depends(get_issue_service),
]

def get_article_service(
    session: SessionDep,
) -> ArticleService:
    return ArticleService(session)


ArticleServiceDep = Annotated[
    ArticleService,
    Depends(get_article_service),
]