# mypy: ignore-errors
"""Main FastAPI application factory."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv  # type: ignore[import-not-found]
from fastapi import FastAPI  # type: ignore[import-not-found]
from fastapi.staticfiles import StaticFiles  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from openai import OpenAI  # type: ignore[import-not-found]
from starlette.middleware.sessions import SessionMiddleware  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]
from starlette.responses import RedirectResponse  # type: ignore[import-not-found]

from exercise_finder.config import get_vector_store_id
from exercise_finder.constants import SESSION_EXPIRATION_SECONDS
from .auth import NotAuthenticatedException, create_auth_router
from .routes import create_main_router
from .api.v1 import create_v1_router


def create_app(
    *,
    exams_root: Path | None = None,
) -> FastAPI:
    """
    Create an ASGI app suitable for local use now and deployment later (e.g. AWS ECS/App Runner).

    Args:
        exams_root: Root directory for exam files. Falls back to EXAMS_ROOT env var.

    The app expects your fixed exam directory structure and serves images from `exams_root`.
    Vector store ID is fetched dynamically via get_vector_store_id() (supports hot reload).
    """
    load_dotenv()
    
    # Validate vector store ID is accessible at startup
    _ = get_vector_store_id()
    
    if exams_root is None:
        exams_root_str = os.environ.get("EXAMS_ROOT")
        if not exams_root_str:
            raise ValueError("exams_root must be provided or EXAMS_ROOT env var must be set")
        exams_root = Path(exams_root_str)
    
    exams_root = exams_root.resolve()
    # web_dir is now the parent of the app folder (exercise_finder/web)
    web_dir = Path(__file__).resolve().parent.parent

    app = FastAPI(title="Exercise Finder", version="0.1.0")
    
    # Add session middleware for authentication
    secret_key = os.getenv("SESSION_SECRET_KEY", "dev-secret-change-in-production")
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        max_age=SESSION_EXPIRATION_SECONDS,  # Cookie expires after 24 hours
    )
    
    # Store OpenAI client and exams root in app state
    app.state.client = OpenAI()
    app.state.exams_root = exams_root

    # Initialize Jinja2 template engine to render HTML templates from the templates directory
    templates = Jinja2Templates(directory=str(web_dir / "templates"))
    app.mount("/static", StaticFiles(directory=str(web_dir / "static")), name="static")

    # Exception handler for authentication errors
    @app.exception_handler(NotAuthenticatedException)
    async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException) -> RedirectResponse:
        """Redirect unauthenticated users to login page."""
        return RedirectResponse(url="/login", status_code=303)

    # Include routers
    auth_router = create_auth_router(templates=templates)
    main_router = create_main_router(templates=templates)
    v1_router = create_v1_router(exams_root=exams_root)
    
    app.include_router(auth_router)
    app.include_router(main_router)
    app.include_router(v1_router)

    return app


# Factory function for uvicorn/gunicorn (reads config from environment)
def app_factory() -> FastAPI:
    """
    Create the app using environment variables.
    
    Used by: uvicorn exercise_finder.web.app:app_factory --factory
    """
    return create_app()

