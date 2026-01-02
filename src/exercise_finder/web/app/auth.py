# mypy: ignore-errors
"""AWS Cognito authentication module."""
from __future__ import annotations

import time

import requests  # type: ignore[import-untyped]
from fastapi import APIRouter, Query  # type: ignore[import-not-found]
from fastapi.responses import HTMLResponse  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from jose import JWTError, jwt  # type: ignore[import-untyped]
from starlette.requests import Request  # type: ignore[import-not-found]
from starlette.responses import RedirectResponse  # type: ignore[import-not-found]

from exercise_finder import paths
from exercise_finder.config import get_cognito_config
from exercise_finder.constants import SESSION_EXPIRATION_SECONDS


class NotAuthenticatedException(Exception):
    """Raised when a user is not authenticated."""
    pass


def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid Cognito session."""
    id_token = request.session.get("id_token")
    if not id_token:
        return False
    
    login_time = request.session.get("login_time")
    if login_time is None:
        request.session.clear()
        return False
    
    if time.time() - login_time > SESSION_EXPIRATION_SECONDS:
        request.session.clear()
        return False
    
    try:
        jwt.decode(id_token, options={"verify_signature": False})
        return True
    except JWTError:
        request.session.clear()
        return False


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
    """Create the authentication router with Cognito OAuth flow."""
    router = APIRouter(tags=["authentication"])
    config = get_cognito_config()

    @router.get("/login", response_model=None)
    async def login(request: Request) -> RedirectResponse | HTMLResponse:
        """Redirect to Cognito hosted UI for login."""
        if is_authenticated(request):
            return RedirectResponse(url="/", status_code=303)
        
        params = {
            "client_id": config.client_id,
            "response_type": "code",
            "scope": "email openid phone",
            "redirect_uri": config.redirect_uri,
        }
        
        cognito_url = paths.cognito_login_url(config.domain, params)
        return RedirectResponse(url=cognito_url, status_code=303)

    @router.get("/callback")
    async def callback(
        request: Request,
        code: str = Query(..., description="Authorization code from Cognito"),
    ) -> RedirectResponse:
        """Handle OAuth callback from Cognito."""
        token_url = paths.cognito_token_url(config.domain)
        
        data = {
            "grant_type": "authorization_code",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": config.redirect_uri,
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            tokens = response.json()
            
            request.session["id_token"] = tokens["id_token"]
            request.session["access_token"] = tokens.get("access_token")
            request.session["refresh_token"] = tokens.get("refresh_token")
            request.session["login_time"] = time.time()
            
            user_info = jwt.decode(tokens["id_token"], options={"verify_signature": False})
            request.session["user_email"] = user_info.get("email")
            request.session["user_name"] = user_info.get("name") or user_info.get("cognito:username")
            
            return RedirectResponse(url="/", status_code=303)
            
        except Exception as e:
            print(f"OAuth callback error: {e}")
            return RedirectResponse(url="/login?error=authentication_failed", status_code=303)

    @router.post("/logout")
    @router.get("/logout")
    async def logout(request: Request) -> RedirectResponse:
        """Clear the session and redirect to Cognito logout."""
        request.session.clear()
        
        params = {
            "client_id": config.client_id,
            "logout_uri": config.redirect_uri.replace("/callback", "/login"),
        }
        
        cognito_logout_url = paths.cognito_logout_url(config.domain, params)
        return RedirectResponse(url=cognito_logout_url, status_code=303)

    return router
