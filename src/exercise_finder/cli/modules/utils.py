"""Shared utilities for CLI commands."""
from __future__ import annotations

# Re-export get_openai_client from config for backward compatibility
from exercise_finder.config import get_openai_client

__all__ = ["get_openai_client"]
