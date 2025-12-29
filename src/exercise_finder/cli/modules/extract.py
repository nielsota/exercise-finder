"""Question extraction commands."""
from __future__ import annotations

from pathlib import Path

import typer  # type: ignore[import-not-found]

from exercise_finder.enums import OpenAIModel
import exercise_finder.paths as paths
from exercise_finder.services.examprocessor.main import process_exam


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
    out_path: Path | None = typer.Option(
        None,
        "--out-path",
        help="Output JSONL path",
    ),
    model: OpenAIModel = typer.Option(
        OpenAIModel.GPT_4O,
        "--model",
        help="Vision model used for transcription.",
        case_sensitive=False,
    ),
) -> None:
    """Convert structured image directory into JSONL (one record per qNN folder)."""

    # default to data/questions-extracted/<exam-dir-name>.jsonl
    if out_path is None:
        out_path = paths.questions_extracted_jsonl(exam_dir.name)

    # process the exam
    process_exam(exam_dir=exam_dir, out_path=out_path, model=model)
