# mypy: ignore-errors
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openai import OpenAI # type: ignore[import-not-found]
from loguru import logger

from exercise_finder.pydantic_models import QuestionRecord

def _load_question_records(jsonl_path: Path) -> list[QuestionRecord]:
    """Load question records from a JSONL file."""
    records: list[QuestionRecord] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(QuestionRecord.model_validate_json(line))
    return records


def _question_record_to_index_text(record: QuestionRecord) -> str:
    """Convert a question record to a text string for indexing.
    
    Example:
    record = QuestionRecord(
        id="123",
        question_text="The answer is 42",
        figure=FigureInfo(present=True, description="A circle with radius 10"),
    )
    return "The answer is 42\n\n[FIGURE]\nA circle with radius 10"
    """
    parts = [record.question_text.strip()]
    if record.figure and record.figure.description:
        parts.append("\n\n[FIGURE]\n" + record.figure.description.strip())
    return "\n".join(parts).strip() + "\n"


def _write_index_files(records: list[QuestionRecord], out_dir: Path) -> dict[str, Path]:
    """Write question records to index files.
    
    Example:
    records = [
        QuestionRecord(id="123", question_text="The answer is 42", figure=FigureInfo(present=True, description="A circle with radius 10")),
    ]
    
    return {
        "123": Path("data/index/123.txt"), # where 123.txt contains the QuestionRecord converted to a text string using _question_record_to_index_text
    }
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    id_to_path: dict[str, Path] = {}
    for record in records:
        path = out_dir / f"{record.id}.txt"
        path.write_text(_question_record_to_index_text(record), encoding="utf-8")
        id_to_path[record.id] = path
    return id_to_path


def _attributes_from_record(record: QuestionRecord) -> dict[str, Any]:
    # record.id is created as f"{exam_id}-q{question_number}" in our pipeline
    exam_id = record.id.rsplit("-q", 1)[0]
    return {
        "record_id": record.id,
        "exam_id": exam_id,
        "exam_level": record.exam.level.value,
        "exam_year": str(record.exam.year),
        "exam_tijdvak": str(record.exam.tijdvak),
        "question_number": str(record.question_number),
        "page_images": json.dumps(record.page_images or [], ensure_ascii=False),
        "figure_images": json.dumps(record.figure_images or [], ensure_ascii=False),
        "source_images": json.dumps(record.source_images or [], ensure_ascii=False),
        "figure_present": str(bool(record.figure.present)),
        "figure_missing": str(bool(record.figure.missing)),
    }


def _save_file_to_openai(*, client: OpenAI, file_path: Path) -> str:
    """Save a file to OpenAI and return the file id."""
    logger.info("Saving file {file_path} to OpenAI", file_path=file_path)
    with file_path.open("rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
    return uploaded.id


def _save_file_to_vector_store(*, client: OpenAI, vector_store_id: str, file_id: str, attributes: dict[str, Any]) -> None:
    """Save a file to a vector store."""
    logger.info("Saving file {file_id} to vector store {vector_store_id}", file_id=file_id, vector_store_id=vector_store_id)
    client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file_id,
        attributes=attributes,
    )