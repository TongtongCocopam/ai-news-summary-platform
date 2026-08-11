from enum import Enum
from http import HTTPStatus


class ErrorCode(Enum):
    USER_ALREADY_EXISTS = (
        HTTPStatus.CONFLICT,
        "USER_ALREADY_EXISTS",
        "이미 가입된 이메일입니다.",
    )

    USER_NOT_FOUND = (
        HTTPStatus.NOT_FOUND,
        "USER_NOT_FOUND",
        "사용자를 찾을 수 없습니다.",
    )

    INVALID_CREDENTIALS = (
        HTTPStatus.UNAUTHORIZED,
        "INVALID_CREDENTIALS",
        "이메일 또는 비밀번호가 올바르지 않습니다.",
    )

    VALIDATION_ERROR = (
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "요청 값이 올바르지 않습니다.",
    )

    DATABASE_UNAVAILABLE = (
        HTTPStatus.SERVICE_UNAVAILABLE,
        "DATABASE_UNAVAILABLE",
        "일시적으로 서비스를 이용할 수 없습니다.",
    )

    INTERNAL_SERVER_ERROR = (
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "INTERNAL_SERVER_ERROR",
        "서버 내부 오류가 발생했습니다.",
    )

    ISSUE_NOT_FOUND = (
        HTTPStatus.NOT_FOUND,
        "NOT_FOUND",
        "이슈를 찾을 수 없습니다.",
    )

    ARTICLE_NOT_FOUND = (
        HTTPStatus.NOT_FOUND,
        "ARTICLE_NOT_FOUND",
        "기사를 찾을 수 없습니다.",
    )

    CATEGORY_NOT_FOUND = (
        HTTPStatus.NOT_FOUND,
        "CATEGORY_NOT_FOUND",
        "카테고리를 찾을 수 없습니다.",
    )

    SUBCATEGORY_NOT_FOUND = (
        HTTPStatus.NOT_FOUND,
        "SUBCATEGORY_NOT_FOUND",
        "해당 카테고리에 속한 서브카테고리를 찾을 수 없습니다.",
    )

    def __init__(
        self,
        status: HTTPStatus,
        code: str,
        message: str,
    ):
        self.status = status
        self.code = code
        self.message = message