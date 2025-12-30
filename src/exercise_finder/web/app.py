# mypy: ignore-errors
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv  # type: ignore[import-not-found]
from fastapi import FastAPI, HTTPException, Form, Depends  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.staticfiles import StaticFiles  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from openai import OpenAI  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]
from starlette.middleware.sessions import SessionMiddleware  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]
from starlette.responses import FileResponse, RedirectResponse  # type: ignore[import-not-found]

from exercise_finder.services.vectorstore.main import vectorstore_fetch
from exercise_finder.services.questionformatter.main import load_formatted_question_from_exam_and_question_number
from exercise_finder.config import get_vector_store_id, refresh_vector_store_id
import exercise_finder.paths as paths

# Session expiration time in seconds (24 hours)
SESSION_EXPIRATION_SECONDS = 24 * 60 * 60


class FetchRequest(BaseModel):
    query: str
    mode: Literal["best", "random"] = "best"
    max_results: int = 5


class NotAuthenticatedException(Exception):
    """Raised when a user is not authenticated."""
    pass


def create_app(
    *,
    exams_root: Path | None = None,
) -> FastAPI:
    """
    Create an ASGI app suitable for local use now and deployment later (e.g. AWS ECS/App Runner).

    Args:
        exams_root: Root directory for exam files. Falls back to EXAMS_ROOT env var.

    The app expects your fixed exam directory structure and serves images from `exams_root`.
    Vector store ID is fetched dynamically via get_vector_store_id() (supports hot reload).
    """
    load_dotenv()
    
    # Validate vector store ID is accessible at startup
    _ = get_vector_store_id()
    
    if exams_root is None:
        exams_root_str = os.environ.get("EXAMS_ROOT")
        if not exams_root_str:
            raise ValueError("exams_root must be provided or EXAMS_ROOT env var must be set")
        exams_root = Path(exams_root_str)
    
    exams_root = exams_root.resolve()
    web_dir = Path(__file__).resolve().parent

    app = FastAPI(title="Exercise Finder", version="0.1.0")
    
    # Add session middleware for authentication
    secret_key = os.getenv("SESSION_SECRET_KEY", "dev-secret-change-in-production")
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        max_age=SESSION_EXPIRATION_SECONDS,  # Cookie expires after 24 hours
    )
    
    app.state.client = OpenAI()
    app.state.exams_root = exams_root

    # Initialize Jinja2 template engine to render HTML templates from the templates directory
    templates = Jinja2Templates(directory=str(web_dir / "templates"))
    app.mount("/static", StaticFiles(directory=str(web_dir / "static")), name="static")

    @app.exception_handler(NotAuthenticatedException)
    async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException) -> RedirectResponse:
        """Redirect unauthenticated users to login page."""
        return RedirectResponse(url="/login", status_code=303)

    @app.get("/login", response_class=HTMLResponse)
    async def login(request: Request) -> HTMLResponse:
        """
        Render the login.html template.
        """
        return templates.TemplateResponse("login.html", {"request": request})


    @app.post("/login", response_model=None)
    async def login_post(request: Request, password: str = Form(...)) -> RedirectResponse | HTMLResponse:
        """
        Handle the login form submission.

        If incorrect, fill the error message in the login template
        Otherwise, set the authenticated flag in the session and redirect to the index page.
        """
        correct_password = os.getenv("APP_PASSWORD")

        if password != correct_password:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Incorrect password"},
                status_code=401,
            )

        # Set authentication with timestamp
        request.session["authenticated"] = True
        request.session["login_time"] = time.time()
        return RedirectResponse(url="/", status_code=303)

    
    @app.post("/logout")
    async def logout(request: Request) -> RedirectResponse:
        """
        Clear the session and redirect to login page.
        """
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    
    def is_authenticated(request: Request) -> bool:
        """
        Check if the user is authenticated and session hasn't expired.
        
        Sessions expire after 24 hours.
        """
        if not request.session.get("authenticated", False):
            return False
        
        # Check if session has expired
        login_time = request.session.get("login_time")
        if login_time is None:
            # Old session without timestamp - invalidate it
            request.session.clear()
            return False
        
        current_time = time.time()
        if current_time - login_time > SESSION_EXPIRATION_SECONDS:
            # Session expired - clear it
            request.session.clear()
            return False
        
        return True


    def require_authentication(request: Request) -> bool:
        """
        Require the user to be authenticated.
        """
        if not is_authenticated(request):
            raise NotAuthenticatedException()
        return True


    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
        """
        Render the index.html template.
        """
        return templates.TemplateResponse("index.html", {"request": request})


    @app.post("/api/fetch")
    async def api_fetch(payload: FetchRequest) -> dict:
        """
        Fetch a question from the vector store.

        This function is called by the app.js script in the static/app.js file.
        """
        query = payload.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Missing query")
        if payload.max_results < 1 or payload.max_results > 20:
            raise HTTPException(status_code=400, detail="max_results must be between 1 and 20")

        vs_id: str = get_vector_store_id()
        
        # Step 1: Search vector store (vectorstore service)
        search_result = await vectorstore_fetch(
            vector_store_id=vs_id,
            query=query,
            max_results=payload.max_results,
            best=(payload.mode == "best"),
        )
        
        # Step 2: Load formatted question (format_questions service)
        formatted_question = load_formatted_question_from_exam_and_question_number(
            exam_id=search_result["exam_id"],
            question_number=search_result["question_number"],
        )
        
        # Step 3: Compose and return
        exam_id = search_result["exam_id"]
        return {
            **search_result,
            "formatted": formatted_question.model_dump(mode="json"),
            "page_images": [f"/image/{exam_id}/{p}" for p in search_result["page_images"]],
            "figure_images": [f"/image/{exam_id}/{p}" for p in search_result["figure_images"]],
        }


    @app.post("/api/refresh-config")
    async def refresh_config(authenticated: bool = Depends(require_authentication)) -> dict:
        """
        Refresh dynamic configuration (e.g., after updating vector store ID in Parameter Store).
        """
        new_vs_id = refresh_vector_store_id()
        return {"message": "Config refreshed", "vector_store_id": new_vs_id}

    @app.get("/image/{exam_id}/{rel_path:path}")
    async def image(exam_id: str, rel_path: str) -> FileResponse:
        # Only allow serving files under the configured exams root:
        #   <exams_root>/<exam_id>/<rel_path>
        candidate = paths.exam_asset_under_root(app.state.exams_root, exam_id, rel_path).resolve()
        try:
            candidate.relative_to(app.state.exams_root)
        except Exception:
            raise HTTPException(status_code=404, detail="Not found")
        if not candidate.exists() or not candidate.is_file():
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(candidate)

    return app


# Factory function for uvicorn/gunicorn (reads config from environment)
def app_factory() -> FastAPI:
    """
    Create the app using environment variables.
    
    Used by: uvicorn exercise_finder.web.app:app_factory --factory
    """
    return create_app()
