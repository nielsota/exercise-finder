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

    @router.get("/practice/unitcircle", response_class=HTMLResponse)
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
        
        return templates.TemplateResponse("practice.html", {
            "request": request,
            "page_title": "Oefenopgaven Eenheidscirkel",
            "page_subtitle": "Leer symmetrieën en periodiciteit door goniometrische vergelijkingen op te lossen",
            "exercises": exercises
        })

    @router.get("/practice/derivatives", response_class=HTMLResponse)
    async def derivatives(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the derivatives exercises page.
        """
        # Derivative practice questions - challenging, no hints
        exercises = [
            {
                "number": 1,
                "exam_id": "CALC-2024-DRV-01",
                "title": "Machtsfuncties",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = 3x^7 - 2x^5 + x^3\)",
                    r"\(g(x) = \frac{2}{x^3} + \frac{5}{x^2}\)",
                    r"\(h(x) = 4\sqrt[3]{x^2} - 3\sqrt{x}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 2,
                "exam_id": "CALC-2024-DRV-02",
                "title": "Goniometrische functies I",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = x^3\sin(x)\)",
                    r"\(g(x) = \cos(x) - x\sin(x)\)",
                    r"\(h(x) = \frac{\sin(x)}{x^2}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 3,
                "exam_id": "CALC-2024-DRV-03",
                "title": "Kettingregel I",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = (3x^2 - 4x + 1)^5\)",
                    r"\(g(x) = \sqrt{x^3 + 2x}\)",
                    r"\(h(x) = \frac{1}{(x^2 + 1)^3}\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 4,
                "exam_id": "CALC-2024-DRV-04",
                "title": "Goniometrische functies II",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = \sin(3x^2)\)",
                    r"\(g(x) = \cos^2(x)\)",
                    r"\(h(x) = \sin(x)\cos(x)\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 5,
                "exam_id": "CALC-2024-DRV-05",
                "title": "Quotiëntregel",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = \frac{x^2 - 1}{x^2 + 1}\)",
                    r"\(g(x) = \frac{2x}{\sqrt{x^2 + 4}}\)",
                    r"\(h(x) = \frac{\sin(x)}{1 + \cos(x)}\)"
                ],
                "max_marks": 12,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 6,
                "exam_id": "CALC-2024-DRV-06",
                "title": "Exponentiële en logaritmische functies",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = xe^x\)",
                    r"\(g(x) = e^{x^2}\)",
                    r"\(h(x) = \ln(x^2 + 1)\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 7,
                "exam_id": "CALC-2024-DRV-07",
                "title": "Kettingregel II",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = \sin^3(2x)\)",
                    r"\(g(x) = e^{\sin(x)}\)",
                    r"\(h(x) = \ln(\cos(x))\)"
                ],
                "max_marks": 12,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 8,
                "exam_id": "CALC-2024-DRV-08",
                "title": "Tangens en cotangens",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = \tan(x)\)",
                    r"\(g(x) = x\tan(x)\)",
                    r"\(h(x) = \tan(x^2 + 1)\)"
                ],
                "max_marks": 9,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 9,
                "exam_id": "CALC-2024-DRV-09",
                "title": "Gemengde opgaven I",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = x^2e^{-x}\)",
                    r"\(g(x) = \frac{\ln(x)}{x}\)",
                    r"\(h(x) = \sqrt{\sin(x) + \cos(x)}\)"
                ],
                "max_marks": 12,
                "calculator_allowed": False,
                "figure_images": []
            },
            {
                "number": 10,
                "exam_id": "CALC-2024-DRV-10",
                "title": "Gemengde opgaven II",
                "question_text": r"Bepaal de afgeleide van de volgende functies.",
                "parts": [
                    r"\(f(x) = \frac{e^x}{\sin(x)}\)",
                    r"\(g(x) = \ln(x^2 + \sqrt{x})\)",
                    r"\(h(x) = (x^2 + 1)^3(x - 2)^2\)"
                ],
                "max_marks": 15,
                "calculator_allowed": False,
                "figure_images": []
            }
        ]
        
        return templates.TemplateResponse("practice.html", {
            "request": request,
            "page_title": "Oefenopgaven Afgeleiden",
            "page_subtitle": "Leer differentiëren met machtsregel, productregel, quotiëntregel en kettingregel",
            "exercises": exercises
        })

    return router

