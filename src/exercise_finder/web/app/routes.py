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
        Render the exercises page with sample data.
        """
        # TODO: Fetch real exercises from your database/vector store
        # For now, use mock data
        exercises = [
            {
                "number": 1,
                "exam_id": "VW-1025-a-19-1-o",
                "title": "Binomial Expansion",
                "question_text": "Expand (2x + 1)⁴ in descending powers of x and simplify your answer.",
                "max_marks": 4,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 2,
                "exam_id": "VW-1025-a-19-1-o",
                "title": "Limit Calculation",
                "question_text": "Calculate the limit of f(x) = (x² - 1)/(x - 1) as x → 1. Show all your working.",
                "max_marks": 5,
                "calculator_allowed": True,
                "figure_images": ["fig1.png"]
            },
            {
                "number": 3,
                "exam_id": "VW-1025-a-19-1-o",
                "title": "Trigonometric Derivative",
                "question_text": "Find the derivative of g(x) = sin(x) · cos(x). Express your answer in its simplest form.",
                "max_marks": 3,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 4,
                "exam_id": "VW-1025-a-19-1-o",
                "title": "Integration",
                "question_text": "Solve the integral ∫(2x + 3)dx. Remember to include the constant of integration.",
                "max_marks": 3,
                "calculator_allowed": True,
                "figure_images": ["fig1.png", "fig2.png"]
            },
            {
                "number": 5,
                "exam_id": "VW-1025-a-19-1-o",
                "title": "Geometric Proof",
                "question_text": "In the diagram below, triangle ABC is isosceles with AB = AC. Prove that the angles at B and C are equal. Use the figures provided to support your proof.",
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": ["triangle.png", "angles.png", "proof.png"]
            }
        ]
        
        return templates.TemplateResponse("exercises.html", {
            "request": request,
            "exercises": exercises
        })

    return router

