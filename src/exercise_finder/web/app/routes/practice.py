# mypy: ignore-errors
"""Practice exercises routes - curated problem sets by topic."""
from __future__ import annotations

from fastapi import APIRouter, Depends  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]

from exercise_finder.pydantic_models import PracticeExerciseSet
import exercise_finder.paths as paths
from ..auth import require_authentication


def create_practice_router(templates: Jinja2Templates) -> APIRouter:
    """
    Create the practice exercises router.
    
    Args:
        templates: Jinja2Templates instance for rendering templates
        
    Returns:
        APIRouter with practice exercise routes
    """
    router = APIRouter()

    @router.get("/unitcircle", response_class=HTMLResponse)
    async def unitcircle(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the unit circle exercises page.
        
        Hand-crafted exercises focusing on unit circle symmetries, periodicity,
        and solving trigonometric equations.
        """
        exercise_set = PracticeExerciseSet.load_from_directory(
            paths.practice_exercise_dir("unitcircle")
        )
        
        return templates.TemplateResponse("practice.html", {
            "request": request,
            "page_title": exercise_set.title,
            "page_subtitle": exercise_set.subtitle,
            "exercises": [
                {
                    "number": i + 1,  # Auto-number from list position
                    "exam_id": ex.exam_id,
                    "title": ex.title,
                    "question_text": ex.stem,
                    "parts": [p.text for p in ex.parts],
                    "max_marks": ex.max_marks,  # Computed property
                    "calculator_allowed": ex.calculator_allowed,
                    "figure_images": ex.figure_images,
                }
                for i, ex in enumerate(exercise_set.exercises)
            ]
        })

    @router.get("/derivatives", response_class=HTMLResponse)
    async def derivatives(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the derivatives exercises page.
        
        Challenging derivative problems covering power rule, product rule,
        quotient rule, and chain rule.
        """
        exercise_set = PracticeExerciseSet.load_from_directory(
            paths.practice_exercise_dir("derivatives")
        )
        
        return templates.TemplateResponse("practice.html", {
            "request": request,
            "page_title": exercise_set.title,
            "page_subtitle": exercise_set.subtitle,
            "exercises": [
                {
                    "number": i + 1,
                    "exam_id": ex.exam_id,
                    "title": ex.title,
                    "question_text": ex.stem,
                    "parts": [p.text for p in ex.parts],
                    "max_marks": ex.max_marks,
                    "calculator_allowed": ex.calculator_allowed,
                    "figure_images": ex.figure_images,
                }
                for i, ex in enumerate(exercise_set.exercises)
            ]
        })

    return router
