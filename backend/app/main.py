import json
import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.controllers import surat_controller, auth_controller
from app.database.db import engine, Base
from app.core.settings import settings
from app.database.models.audit_log_model import AuditLogModel
from app.database.models.user_model import UserModel
from app.database.models.surat_model import SuratModel
from app.database.models.signature_model import SignatureModel
from app.domain.exceptions import DomainException
from app.utils.rate_limiter import InMemoryRateLimiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agridesk API")
app.state.rate_limiter = InMemoryRateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)

logging.basicConfig(level=logging.INFO)
request_logger = logging.getLogger("agridesk.request")


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    if settings.rate_limit_enabled and request.url.path not in {"/health", "/ready"}:
        client_host = request.client.host if request.client else "unknown"
        allowed, remaining, retry_after = app.state.rate_limiter.check(client_host)
        request.state.rate_limit_remaining = remaining
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Remaining": "0",
                },
            )

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    request_logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )
    )
    response.headers["X-Request-ID"] = request_id
    if settings.rate_limit_enabled and request.url.path not in {"/health", "/ready"}:
        remaining = getattr(request.state, "rate_limit_remaining", 0)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/")
def root():
    return {"message": "Agridesk API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})


app.include_router(auth_controller.router)
app.include_router(surat_controller.router)