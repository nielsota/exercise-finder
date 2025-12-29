from pathlib import Path
import json

from loguru import logger

from exercise_finder.pydantic_models import QuestionRecord
from exercise_finder.enums import OpenAIModel
from exercise_finder.agents.format_multipart import format_multipart_question
from exercise_finder.pydantic_models import MultipartQuestionOutput



def _load_question_records_from_jsonl(jsonl_path: Path) -> list[QuestionRecord]:
    """Load question records from a JSONL file."""
    records: list[QuestionRecord] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f: # type: ignore[attr-defined]
            line = line.strip()
            if not line:
                continue
            records.append(QuestionRecord.model_validate_json(line))
    return records

async def _format_question(
    *,
    question_text: str,
    model: OpenAIModel,
) -> MultipartQuestionOutput:
    """
    Format a question text into a multipart question.
    """
    logger.info(f"Formatting question text: {question_text}")
    formatted = await format_multipart_question(question_text=question_text, model=model)
    return formatted


def _save_formatted_question(
    *,
    formatted_question: MultipartQuestionOutput,
    out_path: Path,
) -> Path:
    """
    Save a formatted question to a file.
    """
    logger.info(f"Saving formatted question to {out_path}")
    with open(out_path, "w") as f:
        json.dump(formatted_question.model_dump(mode="json"), f)
    return out_path
