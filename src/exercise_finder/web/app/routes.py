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
                "title": "Basis: Sinus in het eerste kwadrant",
                "question_text": r"Los de vergelijking \(\sin(x) = \frac{1}{2}\) op voor \(0 \leq x \leq 2\pi\). Geef alle oplossingen exact in radialen.",
                "max_marks": 3,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 2,
                "exam_id": "TRIG-2024-UC-02",
                "title": "Symmetrie: Negatieve waarde",
                "question_text": r"Los de vergelijking \(\sin(x) = -\frac{1}{2}\) op voor \(0 \leq x \leq 2\pi\). Leg uit hoe je de symmetrie van de eenheidscirkel gebruikt om alle oplossingen te vinden.",
                "max_marks": 4,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 3,
                "exam_id": "TRIG-2024-UC-03",
                "title": "Cosinus: Horizontale symmetrie",
                "question_text": r"Los de vergelijking \(\cos(x) = \frac{\sqrt{3}}{2}\) op voor \(0 \leq x \leq 2\pi\). Beschrijf de symmetrie-as die je gebruikt om de tweede oplossing te vinden.",
                "max_marks": 4,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 4,
                "exam_id": "TRIG-2024-UC-04",
                "title": "Uitgebreid interval: Periodiciteit",
                "question_text": r"Los de vergelijking \(\sin(x) = \frac{\sqrt{2}}{2}\) op voor \(0 \leq x \leq 4\pi\). Leg uit hoe periodiciteit van de sinusfunctie je helpt om alle vier de oplossingen te vinden.",
                "max_marks": 5,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png", "sine-graph.png"]
            },
            {
                "number": 5,
                "exam_id": "TRIG-2024-UC-05",
                "title": "Kwadrantenanalyse",
                "question_text": r"Los de vergelijking \(\cos(x) = -\frac{1}{2}\) op voor \(0 \leq x \leq 2\pi\). Bepaal eerst in welke kwadranten cosinus negatief is, en gebruik dan symmetrie.",
                "max_marks": 5,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 6,
                "exam_id": "TRIG-2024-UC-06",
                "title": "Smal interval: Beperkte oplossingen",
                "question_text": r"Los de vergelijking \(\sin(x) = \frac{\sqrt{3}}{2}\) op voor \(0 \leq x \leq \pi\). Leg uit waarom er slechts één oplossing is in dit interval.",
                "max_marks": 3,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 7,
                "exam_id": "TRIG-2024-UC-07",
                "title": "Bijzondere waarden: Grensgevallen",
                "question_text": r"Los de vergelijking \(\sin(x) = 1\) op voor \(0 \leq x \leq 4\pi\). Hoeveel oplossingen zijn er? Waarom ligt dit getal lager dan bij andere opgaven?",
                "max_marks": 4,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png"]
            },
            {
                "number": 8,
                "exam_id": "TRIG-2024-UC-08",
                "title": "Synthese: Alle symmetrieën",
                "question_text": r"Los de vergelijking \(\cos(x) = -\frac{\sqrt{2}}{2}\) op voor \(0 \leq x \leq 4\pi\). Beschrijf stap voor stap welke symmetrieën en periodiciteit je gebruikt.",
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": ["unit-circle.png", "cosine-graph.png"]
            }
        ]
        
        return templates.TemplateResponse("exercises.html", {
            "request": request,
            "exercises": exercises
        })

    return router

