# mypy: ignore-errors
"""Web UI routes - serves HTML pages."""
from __future__ import annotations

from fastapi import APIRouter, Depends  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]

from .auth import require_authentication


def create_main_router(templates: Jinja2Templates) -> APIRouter:
    """
    Create the main web UI router.
    
    Args:
        templates: Jinja2Templates instance for rendering templates
        
    Returns:
        APIRouter with web UI routes
    """
    router = APIRouter(tags=["ui"])

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the main application page.
        """
        return templates.TemplateResponse("index.html", {"request": request})

    @router.get("/exercises", response_class=HTMLResponse)
    async def exercises(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the exercises page.
        """
        return templates.TemplateResponse("exercises.html", {"request": request})

    return router

