# mypy: ignore-errors
"""Exam question finder routes - the main search interface."""
from __future__ import annotations

from fastapi import APIRouter, Depends  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]

from ..auth import require_authentication


def create_exam_finder_router(templates: Jinja2Templates) -> APIRouter:
    """
    Create the exam question finder router.
    
    Args:
        templates: Jinja2Templates instance for rendering templates
        
    Returns:
        APIRouter with exam finder routes
    """
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the exam question finder page.
        
        This is the main application page where users can search for exam questions
        by entering a query or requesting a random question.
        """
        return templates.TemplateResponse("index.html", {"request": request})

    return router

