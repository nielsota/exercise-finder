# mypy: ignore-errors
from __future__ import annotations

from pathlib import Path
from typing import Any

from openai import OpenAI # type: ignore[import-not-found]
from loguru import logger

from exercise_finder.pydantic_models import QuestionRecord


def write_index_files(records: list[QuestionRecord], out_dir: Path) -> dict[str, Path]:
    """Write question records to index files.
    
    Args:
        records: List of question records to write to index files.
        out_dir: Directory to write the index files to.

    Returns:
        Dictionary mapping record IDs to their corresponding index file paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    id_to_path: dict[str, Path] = {}
    for record in records:
        path = out_dir / f"{record.id}.txt"
        path.write_text(record.to_text(), encoding="utf-8")
        id_to_path[record.id] = path
    return id_to_path


def save_file_to_openai(*, client: OpenAI, file_path: Path) -> str:
    """Save a file to OpenAI and return the file id."""
    logger.info("Saving file {file_path} to OpenAI", file_path=file_path)
    with file_path.open("rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
    return uploaded.id


def save_file_to_vector_store(*, client: OpenAI, vector_store_id: str, file_id: str, attributes: dict[str, Any]) -> None:
    """Save a file to a vector store."""
    logger.info("Saving file {file_id} to vector store {vector_store_id}", file_id=file_id, vector_store_id=vector_store_id)
    client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file_id,
        attributes=attributes,
    )