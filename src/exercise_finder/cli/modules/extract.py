"""Question extraction commands."""
from __future__ import annotations

from pathlib import Path

import typer  # type: ignore[import-not-found]

from exercise_finder.enums import OpenAIModel
import exercise_finder.paths as paths
from exercise_finder.services.examprocessor.main import process_exam


app = typer.Typer(help="Extract questions from images")


def _process_exam_images(
    exam_dir: Path,
    out_dir: Path | None = None,
    model: OpenAIModel = OpenAIModel.GPT_4O,
) -> None:
    """Internal helper to process exam images. Can be called programmatically."""
    # default to data/questions-extracted/
    if out_dir is None:
        out_dir = paths.questions_extracted_dir()

    # process the exam
    process_exam(exam_dir=exam_dir, out_dir=out_dir, model=model)


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
    out_dir: Path | None = typer.Option(
        None,
        "--out-dir",
        help="Output directory for YAML files (default: data/questions-extracted/)",
    ),
    model: OpenAIModel = typer.Option(
        OpenAIModel.GPT_4O,
        "--model",
        help="Vision model used for transcription.",
        case_sensitive=False,
    ),
) -> None:
    """Convert structured image directory into YAML files (one YAML per question)."""
    _process_exam_images(exam_dir=exam_dir, out_dir=out_dir, model=model)


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
        
        typer.echo(f"Processing exam directory: {exam_dir.name}")
        _process_exam_images(exam_dir=exam_dir)