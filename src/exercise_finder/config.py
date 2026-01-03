# mypy: ignore-errors
"""Configuration management using Pydantic Settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import boto3  # type: ignore[import-untyped]
from pydantic import Field  # type: ignore[import-untyped]
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore[import-untyped]


class CognitoConfig(BaseSettings):
    """AWS Cognito OAuth configuration."""
    
    model_config = SettingsConfigDict(env_prefix="COGNITO_", env_file=".env", extra="ignore")
    
    domain: str = Field(..., description="Cognito domain (e.g., app.auth.region.amazoncognito.com)")
    client_id: str = Field(..., description="Cognito app client ID")
    client_secret: str = Field(..., description="Cognito app client secret")
    user_pool_id: str = Field(..., description="Cognito user pool ID (e.g., us-east-1_xxxxxx)")
    region: str = Field(default="us-east-1", description="AWS region")
    redirect_uri: str = Field(default="http://localhost:8000/callback", description="OAuth callback URL")


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    
    is_production: bool = Field(default=False, description="Whether the application is in production")
    openai_api_key: str = Field(..., description="OpenAI API key")
    session_secret_key: str = Field(..., description="Secret key for session cookies")
    exams_root: Path = Field(default=Path("data/questions-images"), description="Root directory for exam images")
    use_ssm: bool = Field(default=False, description="Use AWS SSM for vector store ID")
    vector_store_id: str | None = Field(default=None, description="OpenAI vector store ID")


@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()


@lru_cache(maxsize=1)
def get_cognito_config() -> CognitoConfig:
    """Get cached Cognito configuration."""
    return CognitoConfig()


def get_vector_store_id() -> str:
    """
    Get the current vector store ID.
    
    Priority:
    1. AWS Parameter Store (if USE_SSM=true)
    2. VECTOR_STORE_ID environment variable
    """
    return _get_vector_store_id_cached()


def refresh_vector_store_id() -> str:
    """Clear cache and fetch fresh vector store ID."""
    _get_vector_store_id_cached.cache_clear()
    return _get_vector_store_id_cached()


@lru_cache(maxsize=1)
def _get_vector_store_id_cached() -> str:
    """Cached fetch of vector store ID."""
    config = get_app_config()
    
    if config.use_ssm:
        return _fetch_from_ssm("/mathwizard-vector-store-id")
    
    if not config.vector_store_id:
        raise ValueError("VECTOR_STORE_ID env var must be set (or enable USE_SSM=true)")
    
    return config.vector_store_id


def _fetch_from_ssm(parameter_name: str) -> str:
    """Fetch a parameter from AWS Systems Manager Parameter Store."""
    ssm = boto3.client("ssm", region_name="us-east-1")
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def update_vector_store_id(new_id: str) -> None:
    """
    Update the vector store ID in AWS Parameter Store.
    
    Args:
        new_id: The new vector store ID to set
        
    Raises:
        ValueError: If USE_SSM is not enabled
    """
    config = get_app_config()
    
    if not config.use_ssm:
        raise ValueError("Cannot update SSM parameter when USE_SSM is not enabled")
    
    ssm = boto3.client("ssm", region_name="us-east-1")
    ssm.put_parameter(
        Name="/mathwizard-vector-store-id",
        Value=new_id,
        Type="String",
        Overwrite=True,
    )
    
    _get_vector_store_id_cached.cache_clear()
