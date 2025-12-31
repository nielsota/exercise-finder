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

    @router.get("/unitcircle", response_class=HTMLResponse)
    async def unitcircle(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the unit circle exercises page.
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
        
        return templates.TemplateResponse("unitcircle.html", {
            "request": request,
            "exercises": exercises
        })

    @router.get("/derivatives", response_class=HTMLResponse)
    async def derivatives(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the derivatives exercises page.
        """
        # Derivative practice questions
        exercises = [
            {
                "number": 1,
                "exam_id": "CALC-2024-DRV-01",
                "title": "Basis: Machtsfuncties",
                "question_text": r"Bepaal de afgeleide van de volgende functies. Gebruik de machtsregel.",
                "parts": [
                    r"\(f(x) = x^3\)",
                    r"\(g(x) = x^5\)",
                    r"\(h(x) = x^{10}\)"
                ],
                "max_marks": 3,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 2,
                "exam_id": "CALC-2024-DRV-02",
                "title": "Constanten en coëfficiënten",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = 5x^2\)",
                    r"\(g(x) = -3x^4\)",
                    r"\(h(x) = \frac{1}{2}x^6\)"
                ],
                "max_marks": 3,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 3,
                "exam_id": "CALC-2024-DRV-03",
                "title": "Somregel",
                "question_text": r"Bepaal de afgeleide van de volgende functies. Pas de somregel toe.",
                "parts": [
                    r"\(f(x) = x^2 + x^3\)",
                    r"\(g(x) = 2x^4 - 3x^2 + 5\)",
                    r"\(h(x) = x^5 - 4x^3 + 2x - 7\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 4,
                "exam_id": "CALC-2024-DRV-04",
                "title": "Negatieve exponenten",
                "question_text": r"Bepaal de afgeleide. Herschrijf eerst als macht met negatieve exponent.",
                "parts": [
                    r"\(f(x) = \frac{1}{x}\)",
                    r"\(g(x) = \frac{1}{x^2}\)",
                    r"\(h(x) = \frac{3}{x^4}\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 5,
                "exam_id": "CALC-2024-DRV-05",
                "title": "Wortelfuncties",
                "question_text": r"Bepaal de afgeleide. Herschrijf eerst als macht met gebroken exponent.",
                "parts": [
                    r"\(f(x) = \sqrt{x}\)",
                    r"\(g(x) = \sqrt[3]{x}\)",
                    r"\(h(x) = 2\sqrt{x} + \frac{1}{\sqrt{x}}\)"
                ],
                "max_marks": 6,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 6,
                "exam_id": "CALC-2024-DRV-06",
                "title": "Productregel",
                "question_text": r"Bepaal de afgeleide met de productregel: \((uv)' = u'v + uv'\).",
                "parts": [
                    r"\(f(x) = x^2 \cdot x^3\) (vereenvoudig eerst!)",
                    r"\(g(x) = (x + 1)(x - 2)\) (vermenigvuldig eerst!)",
                    r"\(h(x) = x^2(3x^2 - 4x + 1)\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 7,
                "exam_id": "CALC-2024-DRV-07",
                "title": "Quotiëntregel",
                "question_text": r"Bepaal de afgeleide met de quotiëntregel: \(\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}\).",
                "parts": [
                    r"\(f(x) = \frac{x^2}{x + 1}\)",
                    r"\(g(x) = \frac{x - 1}{x + 1}\)",
                    r"\(h(x) = \frac{2x^2 + 3}{x^2 - 1}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 8,
                "exam_id": "CALC-2024-DRV-08",
                "title": "Kettingregel",
                "question_text": r"Bepaal de afgeleide met de kettingregel: \(\frac{d}{dx}f(g(x)) = f'(g(x)) \cdot g'(x)\).",
                "parts": [
                    r"\(f(x) = (x^2 + 1)^3\)",
                    r"\(g(x) = (2x - 1)^5\)",
                    r"\(h(x) = \sqrt{x^2 + 4}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 9,
                "exam_id": "CALC-2024-DRV-09",
                "title": "Goniometrische functies",
                "question_text": r"Bepaal de afgeleide. Gebruik \(\frac{d}{dx}\sin(x) = \cos(x)\) en \(\frac{d}{dx}\cos(x) = -\sin(x)\).",
                "parts": [
                    r"\(f(x) = \sin(x) + \cos(x)\)",
                    r"\(g(x) = 3\sin(x) - 2\cos(x)\)",
                    r"\(h(x) = x^2\sin(x)\) (gebruik productregel)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 10,
                "exam_id": "CALC-2024-DRV-10",
                "title": "Synthese: Gemengde opgaven",
                "question_text": r"Bepaal de afgeleide. Gebruik de juiste regels en vereenvoudig je antwoord.",
                "parts": [
                    r"\(f(x) = (x^2 + 1)(x^3 - 2x)\)",
                    r"\(g(x) = \frac{x^2}{\sqrt{x}}\) (vereenvoudig eerst!)",
                    r"\(h(x) = \sin(x^2 + 1)\) (gebruik kettingregel)"
                ],
                "max_marks": 12,
                "calculator_allowed": False,
                "figure_images": []
            }
        ]
        
        return templates.TemplateResponse("derivatives.html", {
            "request": request,
            "exercises": exercises
        })

    return router

