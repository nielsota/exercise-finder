# mypy: ignore-errors
"""Practice exercises routes - curated problem sets by topic."""
from __future__ import annotations

from fastapi import APIRouter, Depends  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]

from exercise_finder.pydantic_models import PracticeExerciseSet, MultipartQuestionOutput
import exercise_finder.paths as paths
from ..auth import require_authentication


def _exercise_to_dict(index: int, ex: MultipartQuestionOutput) -> dict:
    """Convert a MultipartQuestionOutput to a template-friendly dict."""
    return {
        "number": index + 1,
        "exam_id": ex.exam_id,
        "title": ex.title,
        "question_text": ex.stem,
        "parts": [p.text for p in ex.parts],
        "max_marks": ex.max_marks,
        "calculator_allowed": ex.calculator_allowed,
        "difficulty": ex.difficulty,
        "figure_images": ex.figure_images,
    }


def create_practice_router(templates: Jinja2Templates) -> APIRouter:
    """
    Create the practice exercises router.
    
    Args:
        templates: Jinja2Templates instance for rendering templates
        
    Returns:
        APIRouter with practice exercise routes
    """
    router = APIRouter()

    def _render_practice_page(request: Request, topic: str) -> HTMLResponse:
        """Render a practice page for the given topic."""
        exercise_set = PracticeExerciseSet.load_from_directory(paths.practice_exercise_dir(topic))
        return templates.TemplateResponse("practice.html", {
            "request": request,
            "page_title": exercise_set.title,
            "page_subtitle": exercise_set.subtitle,
            "exercises": [_exercise_to_dict(i, ex) for i, ex in enumerate(exercise_set.exercises)]
        })

    @router.get("/unitcircle", response_class=HTMLResponse)
    async def unitcircle(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """Render the unit circle exercises page."""
        return _render_practice_page(request, "unitcircle")

    @router.get("/derivatives", response_class=HTMLResponse)
    async def derivatives(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """Render the derivatives exercises page."""
        return _render_practice_page(request, "derivatives")

    @router.get("/rootfinding", response_class=HTMLResponse)
    async def rootfinding(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """Render the root finding exercises page."""
        return _render_practice_page(request, "rootfinding")

    @router.get("/parametric", response_class=HTMLResponse)
    async def parametric(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """Render the parametric equations exercises page."""
        return _render_practice_page(request, "parametric")

    @router.get("/goniometrie", response_class=HTMLResponse)
    async def goniometrie(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """Render the trigonometry exercises page."""
        return _render_practice_page(request, "goniometrie")

    return router
