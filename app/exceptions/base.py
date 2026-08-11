from app.exceptions.error_code import ErrorCode


class AppException(Exception):

    def __init__(
        self,
        error_code: ErrorCode,
        details: object | None = None,
    ):
        self.error_code = error_code
        self.details = details

        super().__init__(error_code.message)