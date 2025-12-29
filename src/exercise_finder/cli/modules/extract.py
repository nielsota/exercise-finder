"""Question extraction commands."""
from __future__ import annotations

from pathlib import Path

import typer  # type: ignore[import-not-found]

from exercise_finder.enums import OpenAIModel
from exercise_finder.services.image_to_question.main import images_to_questions


app = typer.Typer(help="Extract questions from images")


@app.command("from-images")
def from_images(
    exam_dir: Path = typer.Option(
        ...,
        "--exam-dir",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Exam directory with qNN/pages/*.png and optional qNN/figures/*.png.",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        help="Output JSONL path (default: data/questions-extracted/<exam-dir-name>.jsonl).",
    ),
    model: OpenAIModel = typer.Option(
        OpenAIModel.GPT_4O,
        "--model",
        help="Vision model used for transcription.",
        case_sensitive=False,
    ),
) -> None:
    """Convert structured image directory into JSONL (one record per qNN folder)."""
    images_to_questions(exam_dir=exam_dir, out=out, model=model)

