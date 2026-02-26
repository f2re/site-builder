# Module: core/exceptions.py | Agent: backend-agent | Task: stage1_backend
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Optional

class APIException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "api_error",
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.detail = detail

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # In production, you might want to log this properly with structlog
    from app.core.logging import logger
    
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "code": "internal_error",
            "message": "An unexpected error occurred."
        },
    )

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "detail": exc.detail
        },
    )

def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
