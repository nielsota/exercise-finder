# mypy: ignore-errors
"""
Configuration management - supports both local env vars and AWS Parameter Store.
"""
from __future__ import annotations

import os
from functools import lru_cache


def get_vector_store_id() -> str:
    """
    Get the current vector store ID.
    
    Priority:
    1. AWS Parameter Store (if USE_SSM=true)
    2. VECTOR_STORE_ID environment variable
    
    Use refresh_vector_store_id() to clear cache and fetch fresh value.
    """
    return _get_vector_store_id_cached()


def refresh_vector_store_id() -> str:
    """Clear cache and fetch fresh vector store ID."""
    _get_vector_store_id_cached.cache_clear()
    return _get_vector_store_id_cached()


@lru_cache(maxsize=1)
def _get_vector_store_id_cached() -> str:
    """Cached fetch of vector store ID."""
    use_ssm = os.environ.get("USE_SSM", "false").lower() == "true"
    
    if use_ssm:
        return _fetch_from_ssm("/mathwizard-vector-store-id")
    
    # Fall back to environment variable
    value = os.environ.get("VECTOR_STORE_ID")
    if not value:
        raise ValueError("VECTOR_STORE_ID env var must be set (or enable USE_SSM=true)")
    return value


def _fetch_from_ssm(parameter_name: str) -> str:
    """Fetch a parameter from AWS Systems Manager Parameter Store."""
    import boto3  # type: ignore[import-not-found]
    
    ssm = boto3.client("ssm")
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
    use_ssm = os.environ.get("USE_SSM", "false").lower() == "true"
    
    if not use_ssm:
        raise ValueError("Cannot update SSM parameter when USE_SSM is not enabled")
    
    import boto3  # type: ignore[import-not-found]
    
    ssm = boto3.client("ssm")
    ssm.put_parameter(
        Name="/mathwizard-vector-store-id",
        Value=new_id,
        Type="String",
        Overwrite=True,
    )
    
    # Clear cache so next call fetches the new value
    _get_vector_store_id_cached.cache_clear()

