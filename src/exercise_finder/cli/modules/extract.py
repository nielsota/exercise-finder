"""Question extraction commands."""
from __future__ import annotations

from pathlib import Path

import typer  # type: ignore[import-not-found]

from exercise_finder.enums import OpenAIModel
import exercise_finder.paths as paths
from exercise_finder.services.examprocessor.main import process_exam
from exercise_finder.pydantic_models import Exam


app = typer.Typer(help="Extract questions from images")


def _process_exam_images(
    exam_dir: Path,
    out_path: Path | None = None,
    model: OpenAIModel = OpenAIModel.GPT_4O,
) -> None:
    """Internal helper to process exam images. Can be called programmatically."""
    # default to data/questions-extracted/<exam-dir-name>.jsonl
    if out_path is None:
        out_path = paths.questions_extracted_jsonl(exam_dir.name)

    # process the exam
    process_exam(exam_dir=exam_dir, out_path=out_path, model=model)


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
    _process_exam_images(exam_dir=exam_dir, out_path=out_path, model=model)


@app.command("refresh-all")
def refresh_all(
    exams_root: Path = typer.Option(
        paths.questions_images_root(),
        "--exams-root",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
) -> None:
    """Refresh all exams in the exams root directory."""
    for exam_dir in exams_root.glob("*"):
        if not exam_dir.is_dir():
            continue
        
        # Only process directories that match exam naming pattern
        try:
            Exam.from_file_path(Path(f"{exam_dir.name}.pdf"))  # use exam class to validate the exam directory
            typer.echo(f"Processing exam directory: {exam_dir.name}")
            _process_exam_images(exam_dir=exam_dir)
        except (ValueError, KeyError, IndexError):
            # Skip directories that don't match exam pattern (e.g., "template")
            typer.echo(f"Skipping non-exam directory: {exam_dir.name}")
            continue