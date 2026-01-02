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
    """Check if the user has a valid Cognito session from cookies."""
    id_token = request.cookies.get("id_token")
    if not id_token:
        return False
    
    login_time_str = request.cookies.get("login_time")
    if not login_time_str:
        return False
    
    try:
        login_time = float(login_time_str)
        if time.time() - login_time > SESSION_EXPIRATION_SECONDS:
            return False
        
        # Validate JWT structure (without signature verification)
        jwt.decode(
            id_token,
            key=None,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iat": False,
                "verify_exp": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
        return True
    except (ValueError, JWTError):
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
            "scope": "email openid",
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
            
            # Store tokens directly in HTTP-only cookies
            response = RedirectResponse(url="/", status_code=303)
            
            # Set secure HTTP-only cookies
            response.set_cookie(
                key="id_token",
                value=tokens["id_token"],
                max_age=SESSION_EXPIRATION_SECONDS,
                httponly=True,
                samesite="lax",
                secure=False,  # Set to True in production with HTTPS
            )
            response.set_cookie(
                key="login_time",
                value=str(int(time.time())),
                max_age=SESSION_EXPIRATION_SECONDS,
                httponly=True,
                samesite="lax",
                secure=False,
            )
            
            return response
            
        except Exception as e:
            print(f"OAuth callback error: {e}")
            return RedirectResponse(url="/login?error=authentication_failed", status_code=303)

    @router.post("/logout")
    @router.get("/logout")
    async def logout(request: Request) -> RedirectResponse:
        """Clear auth cookies and redirect to Cognito logout."""
        params = {
            "client_id": config.client_id,
            "logout_uri": config.redirect_uri.replace("/callback", "/login"),
        }
        
        cognito_logout_url = paths.cognito_logout_url(config.domain, params)
        response = RedirectResponse(url=cognito_logout_url, status_code=303)
        
        # Delete auth cookies
        response.delete_cookie("id_token")
        response.delete_cookie("login_time")
        
        return response

    return router
