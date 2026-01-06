"""Tests for configuration management."""
from pathlib import Path
from unittest.mock import patch

import pytest  # type: ignore[import-not-found]
from pydantic import ValidationError  # type: ignore[import-not-found]

from exercise_finder.config import ( # type: ignore[import-not-found]
    AppConfig,
    CognitoConfig,
    get_app_config,
    get_cognito_config,
)


class TestCognitoConfig:
    """Test Cognito configuration model."""

    def test_valid_config(self):
        """Valid configuration should instantiate correctly."""
        config = CognitoConfig(
            _env_file=None,  # Don't load from .env during tests
            domain="test.auth.us-east-1.amazoncognito.com",
            client_id="test-client-id",
            client_secret="test-secret",
            user_pool_id="us-east-1_testpool",
            region="us-east-1",
            redirect_uri="http://localhost:8000/callback",
        )
        
        assert config.domain == "test.auth.us-east-1.amazoncognito.com"
        assert config.client_id == "test-client-id"
        assert config.client_secret == "test-secret"
        assert config.user_pool_id == "us-east-1_testpool"
        assert config.region == "us-east-1"
        assert config.redirect_uri == "http://localhost:8000/callback"

    def test_default_values(self):
        """Default values should be applied."""
        config = CognitoConfig(
            _env_file=None,
            domain="test.auth.us-east-1.amazoncognito.com",
            client_id="test-client-id",
            client_secret="test-secret",
            user_pool_id="us-east-1_testpool",
        )
        
        assert config.region == "us-east-1"
        assert config.redirect_uri == "http://localhost:8000/callback"

    def test_missing_required_field(self):
        """Missing required fields should raise ValidationError."""
        # Clear any COGNITO_* env vars that might be set
        env_vars = {
            k: v for k, v in __import__("os").environ.items()
            if not k.startswith("COGNITO_")
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                CognitoConfig(
                    _env_file=None,
                    domain="test.auth.us-east-1.amazoncognito.com",
                    # Missing client_id, client_secret, and user_pool_id
                )
            
            error = exc_info.value
            assert "client_id" in str(error)
            assert "client_secret" in str(error)
            assert "user_pool_id" in str(error)

    def test_loads_from_env(self):
        """Config should load from environment variables with prefix."""
        env_vars = {
            "COGNITO_DOMAIN": "env.auth.us-east-1.amazoncognito.com",
            "COGNITO_CLIENT_ID": "env-client-id",
            "COGNITO_CLIENT_SECRET": "env-secret",
            "COGNITO_USER_POOL_ID": "us-east-1_envpool",
            "COGNITO_REGION": "eu-west-1",
            "COGNITO_REDIRECT_URI": "https://example.com/callback",
        }
        
        with patch.dict("os.environ", env_vars, clear=False):
            # Clear cache to force reload
            get_cognito_config.cache_clear()
            config = get_cognito_config()
            
            assert config.domain == "env.auth.us-east-1.amazoncognito.com"
            assert config.client_id == "env-client-id"
            assert config.user_pool_id == "us-east-1_envpool"
            assert config.region == "eu-west-1"
            assert config.redirect_uri == "https://example.com/callback"


class TestAppConfig:
    """Test main application configuration model."""

    def test_valid_config(self):
        """Valid configuration should instantiate correctly."""
        config = AppConfig(
            _env_file=None,
            openai_api_key="sk-test",
            session_secret_key="secret",
            exams_root=Path("test/path"),
            use_ssm=True,
            vector_store_id="vs_123",
        )
        
        assert config.openai_api_key == "sk-test"
        assert config.session_secret_key == "secret"
        assert config.exams_root == Path("test/path")
        assert config.use_ssm is True
        assert config.vector_store_id == "vs_123"

    def test_default_values(self):
        """Default values should be applied."""
        # Explicitly pass defaults to override any env vars
        config = AppConfig(
            _env_file=None,
            openai_api_key="sk-test",
            session_secret_key="secret",
            use_ssm=False,
            vector_store_id=None,
        )
        
        assert config.exams_root == Path("data/questions-images")
        assert config.use_ssm is False
        assert config.vector_store_id is None

    def test_missing_required_fields(self):
        """Missing required fields should raise ValidationError."""
        # Clear any relevant env vars that might be set
        env_vars = {
            k: v for k, v in __import__("os").environ.items()
            if k not in ["OPENAI_API_KEY", "SESSION_SECRET_KEY", "VECTOR_STORE_ID"]
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                AppConfig(_env_file=None)
            
            error = exc_info.value
            assert "openai_api_key" in str(error)
            assert "session_secret_key" in str(error)

    def test_loads_from_env(self):
        """Config should load from environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "sk-env-test",
            "SESSION_SECRET_KEY": "env-secret",
            "EXAMS_ROOT": "env/path",
            "USE_SSM": "true",
            "VECTOR_STORE_ID": "vs_env",
        }
        
        with patch.dict("os.environ", env_vars, clear=False):
            # Clear cache to force reload
            get_app_config.cache_clear()
            config = get_app_config()
            
            assert config.openai_api_key == "sk-env-test"
            assert config.session_secret_key == "env-secret"
            assert config.exams_root == Path("env/path")
            assert config.use_ssm is True
            assert config.vector_store_id == "vs_env"

    def test_boolean_parsing(self):
        """USE_SSM should parse various boolean representations."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ]
        
        for env_value, expected in test_cases:
            env_vars = {
                "OPENAI_API_KEY": "sk-test",
                "SESSION_SECRET_KEY": "secret",
                "USE_SSM": env_value,
            }
            
            with patch.dict("os.environ", env_vars, clear=True):
                config = AppConfig()
                assert config.use_ssm is expected, f"Failed for USE_SSM={env_value}"

    def test_path_parsing(self):
        """EXAMS_ROOT should be parsed as Path."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test",
            "SESSION_SECRET_KEY": "secret",
            "EXAMS_ROOT": "data/test/path",
        }
        
        with patch.dict("os.environ", env_vars, clear=False):
            get_app_config.cache_clear()
            config = get_app_config()
            
            assert isinstance(config.exams_root, Path)
            assert config.exams_root == Path("data/test/path")


class TestConfigCaching:
    """Test configuration caching behavior."""

    def test_cognito_config_is_cached(self):
        """get_cognito_config() should return cached instance."""
        env_vars = {
            "COGNITO_DOMAIN": "test.auth.us-east-1.amazoncognito.com",
            "COGNITO_CLIENT_ID": "test-client",
            "COGNITO_CLIENT_SECRET": "test-secret",
            "COGNITO_USER_POOL_ID": "us-east-1_testpool",
        }
        
        with patch.dict("os.environ", env_vars, clear=False):
            get_cognito_config.cache_clear()
            
            config1 = get_cognito_config()
            config2 = get_cognito_config()
            
            # Same instance (cached)
            assert config1 is config2

    def test_app_config_is_cached(self):
        """get_app_config() should return cached instance."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test",
            "SESSION_SECRET_KEY": "secret",
        }
        
        with patch.dict("os.environ", env_vars, clear=False):
            get_app_config.cache_clear()
            
            config1 = get_app_config()
            config2 = get_app_config()
            
            # Same instance (cached)
            assert config1 is config2

    def test_cache_can_be_cleared(self):
        """Cache should be clearable to reload config."""
        env_vars = {
            "OPENAI_API_KEY": "sk-test",
            "SESSION_SECRET_KEY": "secret",
        }
        
        with patch.dict("os.environ", env_vars, clear=False):
            get_app_config.cache_clear()
            config1 = get_app_config()
            
            # Clear cache
            get_app_config.cache_clear()
            config2 = get_app_config()
            
            # Different instances (cache was cleared)
            assert config1 is not config2
            # But same values
            assert config1.openai_api_key == config2.openai_api_key

