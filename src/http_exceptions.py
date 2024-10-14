from starlette.exceptions import HTTPException


class ServiceUnavailableException(HTTPException):
    def __init__(
            self,
            status_code: int = 503,
            detail: str = "Service unavailable, try later"
    ):
        super().__init__(status_code=status_code, detail=detail)