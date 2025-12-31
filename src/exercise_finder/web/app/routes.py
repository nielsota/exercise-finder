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
        # Hand-crafted exercises about unit circle symmetries
        exercises = [
            {
                "number": 1,
                "exam_id": "TRIG-2024-UC-01",
                "title": "Basis: Sinus vergelijkingen",
                "question_text": r"Los de volgende vergelijkingen op voor \(0 \leq x \leq 2\pi\). Geef alle oplossingen exact in radialen.",
                "parts": [
                    r"\(\sin(x) = \frac{1}{2}\)",
                    r"\(\sin(x) = \frac{\sqrt{3}}{2}\)",
                    r"\(\sin(x) = \frac{\sqrt{2}}{2}\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 2,
                "exam_id": "TRIG-2024-UC-02",
                "title": "Symmetrie: Negatieve waarden",
                "question_text": r"Los de volgende vergelijkingen op voor \(0 \leq x \leq 2\pi\). Leg bij elk onderdeel uit welke symmetrie je gebruikt.",
                "parts": [
                    r"\(\sin(x) = -\frac{1}{2}\)",
                    r"\(\cos(x) = -\frac{1}{2}\)",
                    r"\(\sin(x) = -\frac{\sqrt{3}}{2}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 3,
                "exam_id": "TRIG-2024-UC-03",
                "title": "Cosinus vergelijkingen",
                "question_text": r"Los de volgende vergelijkingen op voor \(0 \leq x \leq 2\pi\).",
                "parts": [
                    r"\(\cos(x) = \frac{\sqrt{3}}{2}\)",
                    r"\(\cos(x) = \frac{1}{2}\)",
                    r"\(\cos(x) = 0\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 4,
                "exam_id": "TRIG-2024-UC-04",
                "title": "Uitgebreid interval: Periodiciteit",
                "question_text": r"Los de volgende vergelijkingen op voor \(0 \leq x \leq 4\pi\). Leg uit hoe periodiciteit je helpt.",
                "parts": [
                    r"\(\sin(x) = \frac{\sqrt{2}}{2}\)",
                    r"\(\cos(x) = \frac{\sqrt{2}}{2}\)"
                ],
                "max_marks": 8,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png", "sine-graph.png"]
            },
            {
                "number": 5,
                "exam_id": "TRIG-2024-UC-05",
                "title": "Kwadrantenanalyse",
                "question_text": r"Bepaal eerst in welke kwadranten de functie negatief is, los dan de vergelijkingen op voor \(0 \leq x \leq 2\pi\).",
                "parts": [
                    r"\(\cos(x) = -\frac{1}{2}\)",
                    r"\(\sin(x) = -\frac{\sqrt{2}}{2}\)",
                    r"\(\cos(x) = -\frac{\sqrt{3}}{2}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 6,
                "exam_id": "TRIG-2024-UC-06",
                "title": "Verschillende intervallen",
                "question_text": r"Los de vergelijking \(\sin(x) = \frac{\sqrt{3}}{2}\) op voor de volgende intervallen:",
                "parts": [
                    r"\(0 \leq x \leq \pi\)",
                    r"\(0 \leq x \leq 2\pi\)",
                    r"\(0 \leq x \leq 4\pi\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 7,
                "exam_id": "TRIG-2024-UC-07",
                "title": "Bijzondere waarden",
                "question_text": r"Los de volgende vergelijkingen op voor \(0 \leq x \leq 4\pi\). Let op: dit zijn grensgevallen!",
                "parts": [
                    r"\(\sin(x) = 1\)",
                    r"\(\cos(x) = 1\)",
                    r"\(\sin(x) = -1\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 8,
                "exam_id": "TRIG-2024-UC-08",
                "title": "Synthese: Alle symmetrieën",
                "question_text": r"Los de volgende vergelijkingen op voor \(0 \leq x \leq 4\pi\). Beschrijf bij elk onderdeel welke symmetrieën en periodiciteit je gebruikt.",
                "parts": [
                    r"\(\cos(x) = -\frac{\sqrt{2}}{2}\)",
                    r"\(\sin(x) = -\frac{1}{2}\)",
                    r"\(\cos(x) = \frac{1}{2}\)"
                ],
                "max_marks": 12,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png", "cosine-graph.png"]
            }
        ]
        
        return templates.TemplateResponse("exercises.html", {
            "request": request,
            "exercises": exercises
        })

    return router

