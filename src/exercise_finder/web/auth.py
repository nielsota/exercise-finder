# mypy: ignore-errors
"""Authentication module for the web application."""
from __future__ import annotations

import os
import time

from fastapi import APIRouter, Form  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]
from starlette.responses import RedirectResponse  # type: ignore[import-not-found]

from exercise_finder.constants import SESSION_EXPIRATION_SECONDS


class NotAuthenticatedException(Exception):
    """Raised when a user is not authenticated."""
    pass


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
    
    Raises:
        NotAuthenticatedException: If the user is not authenticated
    """
    if not is_authenticated(request):
        raise NotAuthenticatedException()
    return True


def create_auth_router(templates: Jinja2Templates) -> APIRouter:
    """
    Create the authentication router.
    
    Args:
        templates: Jinja2Templates instance for rendering templates
        
    Returns:
        APIRouter with authentication routes
    """
    router = APIRouter(tags=["authentication"])

    @router.get("/login", response_class=HTMLResponse)
    async def login(request: Request) -> HTMLResponse:
        """
        Render the login.html template.
        """
        return templates.TemplateResponse("login.html", {"request": request})

    @router.post("/login", response_model=None)
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

    @router.post("/logout")
    async def logout(request: Request) -> RedirectResponse:
        """
        Clear the session and redirect to login page.
        """
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    return router

