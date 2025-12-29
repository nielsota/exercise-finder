"""Extract questions from structured exam image directories."""
from __future__ import annotations

import json
from pathlib import Path
import asyncio

from loguru import logger

from exercise_finder.enums import OpenAIModel
from exercise_finder.utils.progressbar import create_progress_bar
from exercise_finder.pydantic_models import QuestionRecord
from exercise_finder.agents.images_to_question import transcribe_question_images
from exercise_finder.services.image_to_question.helpers import (
    _exam_from_exam_dir,
    _iter_question_dirs,
    _parse_question_number,
    get_pages_and_figures_from_question_dir,
    paths_relative_to,
)
import exercise_finder.paths as paths


async def process_question(
    *,
    question_dir: Path,
    exam_dir: Path,
    model: OpenAIModel,
) -> QuestionRecord:
    """
    Process a single question directory into a QuestionRecord.
    
    Args:
        question_dir: Path to question directory (e.g., q01/)
        exam_dir: Parent exam directory (for relative path calculation)
        model: OpenAI model to use for transcription
        
    Returns:
        QuestionRecord with transcribed text and image paths
        
    Example:
        >>> exam_dir = Path("data/questions-images/VW-1025-a-18-1-o")
        >>> question_dir = exam_dir / "q01"
        >>> record = await process_question(
        ...     question_dir=question_dir,
        ...     exam_dir=exam_dir,
        ...     model=OpenAIModel.GPT_4O,
        ... )
        >>> record.question_number
        '1'
        >>> record.page_images
        ['q01/pages/page1.png', 'q01/pages/page2.png']
    """
    # Parse question number from directory name (q01 -> "1")
    question_number = _parse_question_number(question_dir.name)
    
    # Get pages and figures
    pages, figures = get_pages_and_figures_from_question_dir(question_dir)
    
    # Transcribe the question using OCR agent
    logger.info(
        "Transcribing question_dir={question_dir} images={n}",
        question_dir=question_dir,
        n=len(pages) + len(figures),
    )
    
    ocr = await transcribe_question_images(
        page_images=pages,
        figure_images=figures,
        model=model,
    )
    
    # Build question record with relative paths
    exam = _exam_from_exam_dir(exam_dir)
    all_images = [*pages, *figures]
    
    return QuestionRecord(
        id=f"{exam_dir.name}-q{question_number}",
        exam=exam,
        question_number=str(question_number),
        question_text=ocr.question_text,
        figure=ocr.figure,
        source_images=paths_relative_to(all_images, exam_dir),
        page_images=paths_relative_to(pages, exam_dir),
        figure_images=paths_relative_to(figures, exam_dir),
    )


async def process_exam_dir(*, exam_dir: Path, out_path: Path, model: OpenAIModel) -> None:
    """
    Process an exam directory of per-question images into question JSONL.
    
    Expected folder structure:
        data/questions-images/<EXAM_STEM>/
          q01/
            pages/        # required: 1+ images containing the question text
              page1.png
              page2.png
            figures/      # optional: diagrams referenced by the question
              fig1.png
          q02/
            pages/
              page3.png
    
    Output:
        Writes JSONL to `out_path` with one `QuestionRecord` per `qNN/` directory.
        Each record includes:
        - `question_text`: verbatim transcription of all parts visible in the images
        - `page_images`/`figure_images`: relative paths (relative to `exam_dir`)
    
    Example:
        >>> exam_dir = Path("data/questions-images/VW-1025-a-18-1-o")
        >>> out_path = Path("data/questions-extracted/VW-1025-a-18-1-o.jsonl")
        >>> await process_exam_dir(
        ...     exam_dir=exam_dir,
        ...     out_path=out_path,
        ...     model=OpenAIModel.GPT_4O,
        ... )
        # Creates out_path with one JSON line per question
    """
    # Create output directory
    out_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Writing JSONL to {out_path}", out_path=out_path)

    # Find all question directories
    question_dirs: list[Path] = _iter_question_dirs(exam_dir)
    logger.info("Found {n} questions", n=len(question_dirs))
    
    # Process each question with progress bar
    with create_progress_bar(f"Processing {exam_dir.name}", total=len(question_dirs)) as (progress, task):
        with out_path.open("w", encoding="utf-8") as f:
            for question_dir in question_dirs:
                try:
                    record = await process_question(
                        question_dir=question_dir,
                        exam_dir=exam_dir,
                        model=model,
                    )
                    f.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False) + "\n")
                    progress.update(task, advance=1, description=f"✓ {exam_dir.name} - q{record.question_number}")
                except ValueError as e:
                    logger.warning("Skipping {question_dir}: {error}", question_dir=question_dir, error=e)
                    progress.update(task, advance=1, description=f"⚠ {exam_dir.name} - {question_dir.name} (skipped)")
                    continue


def images_to_questions(*, exam_dir: Path, out: Path | None, model: OpenAIModel) -> None:
    """
    CLI entry point: Process exam directory synchronously.
    
    Args:
        exam_dir: Path to exam directory
        out: Output JSONL path (defaults to data/questions-extracted/<exam-name>.jsonl)
        model: OpenAI model to use
    """
    if out is None:
        out = paths.questions_extracted_dir() / f"{exam_dir.name}.jsonl"
    
    asyncio.run(process_exam_dir(exam_dir=exam_dir, out_path=out, model=model))
