"""Question formatting commands."""
from __future__ import annotations

from pathlib import Path

import typer  # type: ignore[import-not-found]

from exercise_finder.enums import OpenAIModel
from exercise_finder.services.questionformatter.main import format_questions
import exercise_finder.paths as paths


app = typer.Typer(help="Format extracted questions")


@app.command("questions")
def format_questions_cmd(
    question_records_dir: Path = typer.Option(
        paths.questions_extracted_dir(),
        "--question-records-dir",
        help="Directory with extracted question JSONL files",
    ),
    out_dir: Path = typer.Option(
        paths.questions_formatted_dir(),
        "--out-dir",
        help="Output directory for formatted questions",
    ),
    model: OpenAIModel = typer.Option(
        OpenAIModel.GPT_5_MINI,
        "--model",
        help="Model to use for formatting",
    ),
) -> None:
    """Format a directory of question texts using a specialized agent."""
    format_questions(
        question_records_dir=question_records_dir,
        out_dir=out_dir,
        model=model,
    )

