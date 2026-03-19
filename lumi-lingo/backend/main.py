import logging
import os
import secrets
import time
from functools import lru_cache

from dotenv import load_dotenv

import uvicorn
from cachetools import TTLCache
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from crud import (
    create_user_progress,
    get_exercise,
    get_exercises,
)
from database import Base, engine, get_db
from schemas import AnswerCheck, AnswerCheckResponse, ExercisePublic
from schemas import UserProgress as UserProgressSchema

# Load environment variables
load_dotenv()


@lru_cache
def get_settings():
    """Load and cache application settings from environment variables."""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "backend_host": os.getenv("BACKEND_HOST", "127.0.0.1"),
        "backend_port": int(os.getenv("BACKEND_PORT", "8000")),
        "database_url": os.getenv("DATABASE_URL", "sqlite:///./lumilingo.db"),
        "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        "secure_cookies": os.getenv("SECURE_COOKIES", "false").lower() == "true",
        "debug": os.getenv("DEBUG", "true").lower() == "true",
    }


settings = get_settings()

# Configure logging based on environment
log_level = "debug" if settings["debug"] else "info"
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info(f"Starting application in {settings['environment']} mode")

# Initialize rate limiter (60 calls per minute)
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per minute"])

app = FastAPI(title="LumiLingo API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    Logs the full error for debugging while returning a safe response to clients.
    """
    logger.exception("Unhandled exception occurred: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Create tables
Base.metadata.create_all(bind=engine)

# Add CORS middleware with restricted configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings["cors_origins"],  # Allow configured origins
    allow_credentials=True,
    allow_methods=[
        "GET", "POST", "PUT", "DELETE", "OPTIONS",
    ],  # Restrict to specific methods
    allow_headers=[
        "Content-Type", "Authorization", "X-CSRF-Token",
    ],  # Restrict to specific headers
    expose_headers=["X-CSRF-Token"],  # Expose CSRF token header
    max_age=600,  # Preflight cache duration (10 minutes)
)

# CSRF token storage with TTL and size limit to prevent unbounded memory growth
# TTL: 86400 seconds (24 hours), Max size: 10000 entries
csrf_tokens = TTLCache(maxsize=10000, ttl=86400)

def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str, session_id: str) -> bool:
    """Validate CSRF token against session."""
    if not session_id or not token:
        return False
    return csrf_tokens.get(session_id) == token

# CSRF middleware - using Starlette's middleware pattern


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware to protect against CSRF attacks for state-changing requests."""

    async def dispatch(self, request, call_next):
        method = request.method.upper()

        # Skip CSRF check for safe methods
        if method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            response = await call_next(request)

            # Add CSRF token to response headers for safe methods
            session_id = request.cookies.get("session_id")
            if session_id:
                # Generate token if not exists
                if session_id not in csrf_tokens:
                    csrf_tokens[session_id] = generate_csrf_token()
                response.headers["x-csrf-token"] = csrf_tokens[session_id]
            else:
                # Generate new session and token
                new_session_id = secrets.token_urlsafe(32)
                new_csrf_token = generate_csrf_token()
                csrf_tokens[new_session_id] = new_csrf_token
                response.headers["x-csrf-token"] = new_csrf_token
                response.set_cookie(
                    key="session_id",
                    value=new_session_id,
                    httponly=True,
                    samesite="strict",
                    secure=settings["secure_cookies"],
                    max_age=86400  # 24 hours
                )

            return response

        # Get session ID from cookie or header
        session_id = (
            request.cookies.get("session_id")
            or request.headers.get("x-session-id")
        )

        # Get CSRF token from header
        csrf_token = request.headers.get("x-csrf-token")

        # For POST/PUT/DELETE requests, validate CSRF token
        if method in ["POST", "PUT", "DELETE"]:
            if not session_id:
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Session ID required for state-changing requests"
                    }
                )

            if not csrf_token:
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "CSRF token required for state-changing requests"
                    }
                )

            if not validate_csrf_token(csrf_token, session_id):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid CSRF token"}
                )

        # Process request
        response = await call_next(request)
        return response

# Add CSRF middleware
app.add_middleware(CSRFMiddleware)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Content-Security-Policy: Control resource loading
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:;"
        )

        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Control browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )

        # Strict-Transport-Security: Enforce HTTPS (only in production)
        if settings["secure_cookies"]:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


app.add_middleware(SecurityHeadersMiddleware)

# Endpoint to get CSRF token
@app.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Endpoint to retrieve CSRF token for the current session."""
    session_id = request.cookies.get("session_id")

    if not session_id:
        # Generate new session and token
        session_id = secrets.token_urlsafe(32)
        csrf_token = generate_csrf_token()
        csrf_tokens[session_id] = csrf_token

        response = JSONResponse(content={"csrf_token": csrf_token})
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="strict",
            secure=settings["secure_cookies"],
            max_age=86400  # 24 hours
        )
        return response

    # Generate token if not exists
    if session_id not in csrf_tokens:
        csrf_tokens[session_id] = generate_csrf_token()

    return {"csrf_token": csrf_tokens[session_id]}


# API Routes
@app.get("/")
@limiter.limit("60 per minute")
async def root(request: Request):
    return {"message": "Welcome to LumiLingo API"}


@app.get("/exercises", response_model=list[ExercisePublic])
@limiter.limit("60 per minute")
async def get_exercises_endpoint(request: Request, db: Session = Depends(get_db)):
    exercises = get_exercises(db)
    # Convert to Pydantic model for response using ORM mode (without answers)
    return [ExercisePublic.model_validate(exercise) for exercise in exercises]


@app.get("/exercises/{exercise_id}", response_model=ExercisePublic)
@limiter.limit("60 per minute")
async def get_exercise_endpoint(
    request: Request, exercise_id: str, db: Session = Depends(get_db)
):
    exercise = get_exercise(db, exercise_id)
    if exercise:
        # Convert to Pydantic model for response using ORM mode (without answer)
        return ExercisePublic.model_validate(exercise)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Exercise not found",
    )


@app.post("/check-answer", response_model=AnswerCheckResponse)
@limiter.limit("30 per minute")
async def check_answer(
    request: Request, answer_check: AnswerCheck, db: Session = Depends(get_db)
):
    """Check if the user's answer is correct (server-side validation)."""
    exercise = get_exercise(db, str(answer_check.exercise_id))
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    # Compare answers (case-insensitive for text-based answers)
    is_correct = (
        exercise.answer.lower().strip()
        == answer_check.user_answer.lower().strip()
    )

    # Calculate score (100 for correct, 0 for incorrect)
    score = 100 if is_correct else 0

    return AnswerCheckResponse(
        is_correct=is_correct,
        explanation=exercise.explanation if is_correct else None,  # type: ignore
        score=score,
    )


@app.post("/progress")
@limiter.limit("30 per minute")
async def update_progress(
    request: Request, progress: UserProgressSchema, db: Session = Depends(get_db)
):
    # In a real app, this would save to a database
    create_user_progress(
        db,
        progress.user_id,
        str(progress.exercise_id),
        progress.completed,
        progress.score,
    )
    return {"message": "Progress updated successfully"}


# Additional endpoint to get language information
@app.get("/languages")
@limiter.limit("60 per minute")
async def get_languages(request: Request, _db: Session = Depends(get_db)):
    # This would be implemented to return language information
    return {"message": "Languages endpoint available"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings["backend_host"],
        port=settings["backend_port"],
        reload=settings["debug"],
        log_level="debug" if settings["debug"] else "info"
    )
