"""Shared utilities for CLI commands."""
from __future__ import annotations

import os

import typer  # type: ignore[import-not-found]
from dotenv import load_dotenv  # type: ignore[import-not-found]
from openai import OpenAI  # type: ignore[import-not-found]


def get_openai_client() -> OpenAI:
    """Get an authenticated OpenAI client."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise typer.BadParameter("Missing OPENAI_API_KEY in environment.")
    return OpenAI(api_key=api_key)

