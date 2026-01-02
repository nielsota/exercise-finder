# mypy: ignore-errors
"""Web UI routes package."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]

from .exam_finder import create_exam_finder_router
from .practice import create_practice_router


def create_main_router(templates: Jinja2Templates) -> APIRouter:
    """
    Create the main web UI router by combining all route modules.
    
    Args:
        templates: Jinja2Templates instance for rendering templates
        
    Returns:
        APIRouter with all web UI routes
    """
    router = APIRouter(tags=["ui"])
    
    # Include exam question finder routes
    exam_finder_router = create_exam_finder_router(templates)
    router.include_router(exam_finder_router)
    
    # Include practice exercises routes
    practice_router = create_practice_router(templates)
    router.include_router(practice_router, prefix="/practice", tags=["practice"])
    
    return router

