# mypy: ignore-errors
"""AWS Cognito authentication using authlib (AWS recommended approach)."""
from __future__ import annotations

from authlib.integrations.starlette_client import OAuth  # type: ignore[import-untyped]
from fastapi import APIRouter  # type: ignore[import-not-found]
from fastapi.templating import Jinja2Templates  # type: ignore[import-not-found]
from starlette.requests import Request  # type: ignore[import-not-found]
from starlette.responses import RedirectResponse  # type: ignore[import-not-found]

from exercise_finder.config import get_cognito_config


class NotAuthenticatedException(Exception):
    """Raised when a user is not authenticated."""
    pass


def _get_oauth() -> OAuth:
    """Create and configure OAuth client for Cognito."""
    config = get_cognito_config()
    oauth = OAuth()
    
    # Cognito OpenID Connect discovery URL
    issuer = f"https://cognito-idp.{config.region}.amazonaws.com/{config.user_pool_id}"
    
    oauth.register(
        name="cognito",
        client_id=config.client_id,
        client_secret=config.client_secret,
        server_metadata_url=f"{issuer}/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email"},
    )
    
    return oauth


def is_authenticated(request: Request) -> bool:
    """Check if the user has a valid session with user info."""
    return request.session.get("user") is not None


def require_authentication(request: Request) -> bool:
    """
    Require the user to be authenticated.
    
    Raises:
        NotAuthenticatedException: If the user is not authenticated
    """
    if not is_authenticated(request):
        raise NotAuthenticatedException()
    return True


def get_user_email(request: Request) -> str | None:
    """Get the authenticated user's email from the session."""
    user = request.session.get("user")
    return user.get("email") if user else None


def create_auth_router(templates: Jinja2Templates) -> APIRouter:
    """Create the authentication router with Cognito OAuth flow."""
    router = APIRouter(tags=["authentication"])
    config = get_cognito_config()
    oauth = _get_oauth()

    @router.get("/login", response_model=None)
    async def login(request: Request) -> RedirectResponse:
        """Redirect to Cognito hosted UI for login."""
        return await oauth.cognito.authorize_redirect(request, config.redirect_uri)

    @router.get("/callback")
    async def callback(request: Request) -> RedirectResponse:
        """Handle OAuth callback from Cognito."""
        try:
            token = await oauth.cognito.authorize_access_token(request)
            
            # Store user info in session (authlib parses the ID token automatically)
            user_info = token.get("userinfo")
            if user_info:
                request.session["user"] = dict(user_info)
            
            return RedirectResponse(url="/", status_code=303)
            
        except Exception as e:
            print(f"OAuth callback error: {e}")
            return RedirectResponse(url="/login?error=auth_failed", status_code=303)

    @router.get("/logout")
    @router.post("/logout")
    async def logout(request: Request) -> RedirectResponse:
        """Clear session and redirect to Cognito logout."""
        request.session.clear()
        
        logout_uri = config.redirect_uri.replace("/callback", "/")
        cognito_logout_url = (
            f"https://{config.domain}/logout"
            f"?client_id={config.client_id}"
            f"&logout_uri={logout_uri}"
        )
        
        return RedirectResponse(url=cognito_logout_url, status_code=303)

    return router
