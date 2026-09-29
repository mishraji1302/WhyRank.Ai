import os
import logging
import time
from collections import defaultdict, deque
from threading import Lock
from pathlib import Path
from dotenv import load_dotenv

# Load backend credentials from the local, gitignored .env file.
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# Keep numerical libraries from oversubscribing native threads on macOS.
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

app = FastAPI(
    title="WhyRank Search API",
    description="Explainable multi-signal Information Retrieval and search ranking system",
    version="1.0.0",
)

logger = logging.getLogger(__name__)
allowed_origins = [origin.strip() for origin in os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler to catch unexpected errors and return structured JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Per-process sliding-window protection for search and mutation routes.
_request_times = defaultdict(deque)
_rate_limit_lock = Lock()
_rate_limit = max(1, int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "120")))


@app.middleware("http")
async def rate_limit_api(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with _rate_limit_lock:
            requests = _request_times[client_ip]
            while requests and now - requests[0] >= 60:
                requests.popleft()
            if len(requests) >= _rate_limit:
                return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"}, headers={"Retry-After": "60"})
            requests.append(now)
    return await call_next(request)

# Register routes during app construction so ASGI transports and TestClient
# expose the same API as a long-running Uvicorn process.
from app.api.documents import router as documents_router
from app.api.search import router as search_router

app.include_router(documents_router)
app.include_router(search_router)

@app.get("/")
def read_root():
    return {
        "app": "WhyRank Search API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "whyrank-backend",
    }
