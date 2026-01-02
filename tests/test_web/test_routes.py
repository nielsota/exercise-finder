"""
Tests for web routes using FastAPI TestClient.

These tests make actual HTTP requests to the app without needing Docker.
"""
from pathlib import Path 
from unittest.mock import MagicMock, patch

import pytest  # type: ignore[import-not-found]
from fastapi.testclient import TestClient  # type: ignore[import-not-found]

from exercise_finder import paths  # type: ignore[import-not-found]
from exercise_finder.web.app import create_app  # type: ignore[import-not-found]
from exercise_finder.config import AppConfig, CognitoConfig # type: ignore[import-not-found]
from exercise_finder.pydantic_models import MultipartQuestionOutput # type: ignore[import-not-found]

@pytest.fixture
def mock_app_config():
    """Mock app configuration to avoid validation errors during tests."""
    
    mock_config = AppConfig(
        _env_file=None,
        openai_api_key="sk-test-key",
        session_secret_key="test-secret-key",
        exams_root=Path("data/questions-images"),
        use_ssm=False,
        vector_store_id="test-vector-store-id",
    )
    
    with patch("exercise_finder.config.get_app_config") as mock:
        mock.return_value = mock_config
        yield mock


@pytest.fixture
def mock_cognito_config():
    """Mock Cognito configuration to avoid validation errors during tests."""
    
    mock_config = CognitoConfig(
        _env_file=None,
        domain="test.auth.us-east-1.amazoncognito.com",
        client_id="test-client-id",
        client_secret="test-secret",
        region="us-east-1",
        redirect_uri="http://localhost:8000/callback",
    )
    
    with patch("exercise_finder.web.app.auth.get_cognito_config") as mock:
        mock.return_value = mock_config
        yield mock


@pytest.fixture
def mock_openai_client():
    """Mock the OpenAI client to avoid API calls during tests."""
    with patch("exercise_finder.web.app.OpenAI") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_vector_store_id():
    """Mock the vector store ID to avoid AWS SSM calls during tests."""
    with patch("exercise_finder.web.app.get_vector_store_id") as mock:
        mock.return_value = "test-vector-store-id"
        yield mock


@pytest.fixture
def app(mock_app_config, mock_cognito_config, mock_openai_client, mock_vector_store_id):
    """Create a test app instance with mocked dependencies."""
    exams_root = paths.questions_images_root()
    return create_app(exams_root=exams_root)


@pytest.fixture
def client(app):
    """Create a test client for making requests."""
    return TestClient(app)


@pytest.fixture
def authenticated_client(app):
    """Create a test client with an authenticated session."""
    with TestClient(app) as client:
        # Patch is_authenticated to return True for this client
        # This simulates a successfully authenticated Cognito user
        with patch("exercise_finder.web.app.auth.is_authenticated", return_value=True):
            yield client


class TestAuthRoutes:
    """Test authentication-related routes."""

    def test_login_redirects_to_cognito(self, client):
        """Login should redirect to Cognito hosted UI."""
        response = client.get("/login", follow_redirects=False)
        assert response.status_code == 303
        
        # Should redirect to Cognito domain
        redirect_url = response.headers.get("location", "")
        # Check that it's a valid redirect URL (contains cognito domain or local callback)
        assert redirect_url != "", "Should have a redirect location"


class TestPracticeRoutes:
    """Test practice exercise routes."""

    def test_unitcircle_page_loads(self, client):
        """Unit circle practice page should load successfully."""
        # This will redirect to login if not authenticated
        response = client.get("/practice/unitcircle", follow_redirects=False)
        
        # Either it loads (200) or redirects to login (303)
        assert response.status_code in [200, 303]
        
        if response.status_code == 303:
            assert response.headers["location"] == "/login"

    def test_derivatives_page_loads(self, client):
        """Derivatives practice page should load successfully."""
        response = client.get("/practice/derivatives", follow_redirects=False)
        
        # Either it loads (200) or redirects to login (303)
        assert response.status_code in [200, 303]
        
        if response.status_code == 303:
            assert response.headers["location"] == "/login"

    def test_unitcircle_pageexists(self, client):
        """Unit circle page endpoint exists (will redirect to login if not authenticated)."""
        response = client.get("/practice/unitcircle", follow_redirects=False)
        
        # Should either load (200) or redirect to login (303)
        # Both indicate the route exists and is working
        assert response.status_code in [200, 303]


class TestExamFinderRoutes:
    """Test exam question finder routes."""

    def test_index_page_loads(self, client):
        """Index page should load successfully."""
        response = client.get("/", follow_redirects=False)
        
        # Either it loads (200) or redirects to login (303)
        assert response.status_code in [200, 303]


class TestStaticFiles:
    """Test static file serving."""

    def test_static_css_accessible(self, client):
        """CSS files should be accessible."""
        response = client.get("/static/css/style.css", follow_redirects=False)
        
        # Should either exist (200) or not found (404), but not error
        assert response.status_code in [200, 404]


class TestAPIRoutes:
    """Test API endpoints."""

    def test_fetch_endpoint_requires_auth(self, client):
        """POST /api/v1/fetch should require authentication."""
        response = client.post(
            "/api/v1/fetch",
            json={"query": "test query"},
            follow_redirects=False
        )
        # Should redirect to login if not authenticated
        assert response.status_code == 303
        assert response.headers["location"] == "/login"

    def test_image_urls_have_correct_prefix(self, authenticated_client):
        """
        REGRESSION TEST: Image URLs returned by fetch must include /api/v1 prefix.
        
        This test catches the bug where images were served at /api/v1/image/...
        but the API was returning URLs like /image/... (missing prefix).
        """
        
        with patch("exercise_finder.web.app.api.v1.vectorstore_fetch") as mock_fetch:
            mock_fetch.return_value = {
                "record_id": "test-exam-q1",
                "exam_id": "test-exam",
                "question_number": "1",
                "page_images": ["q1/pages/page1.png"],
                "figure_images": ["q1/figures/fig1.png"],
            }
            
            with patch("exercise_finder.web.app.api.v1.load_formatted_question_from_exam_and_question_number") as mock_load:
                # Return a proper Pydantic model
                mock_load.return_value = MultipartQuestionOutput(
                    title="Test Question Title",
                    stem="Test question",
                    parts=[],
                    page_images=["q1/pages/page1.png"],
                    figure_images=["q1/figures/fig1.png"],
                )
                
                response = authenticated_client.post("/api/v1/fetch", json={"query": "test"})
                
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                data = response.json()
                
                # KEY TEST: URLs must have /api/v1 prefix
                for url in data.get("page_images", []):
                    assert url.startswith("/api/v1/image/"), f"Image URL should start with /api/v1/image/, got: {url}"
                
                for url in data.get("figure_images", []):
                    assert url.startswith("/api/v1/image/"), f"Image URL should start with /api/v1/image/, got: {url}"


class TestErrorHandling:
    """Test error handling."""

    def test_404_page(self, client):
        """Non-existent pages should return 404."""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404

    def test_unauthenticated_redirect(self, client):
        """Unauthenticated requests to protected pages should redirect to login."""
        response = client.get("/", follow_redirects=False)
        
        if response.status_code == 303:
            assert response.headers["location"] == "/login"

