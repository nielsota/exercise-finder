"""Extract questions from structured exam image directories."""
from __future__ import annotations

import json
from pathlib import Path
import asyncio

from loguru import logger

from exercise_finder.enums import OpenAIModel
from exercise_finder.utils.progressbar import create_progress_bar
from exercise_finder.pydantic_models import QuestionRecord, ExamFolderStructure, QuestionFolderStructure
from exercise_finder.agents.images_to_question import transcribe_question_images



async def process_question(
    *,
    question: QuestionFolderStructure,
    exam: ExamFolderStructure,
    model: OpenAIModel,
) -> QuestionRecord:
    """
    Process a single question directory into a QuestionRecord.
    
    Args:
        question: Validated question folder structure
        exam: Validated exam folder structure (contains exam metadata and root path)
        model: OpenAI model to use for transcription
        
    Returns:
        QuestionRecord with transcribed text and image paths
        
    Example:
        >>> exam = ExamFolderStructure.from_exam_dir(Path("data/questions-images/VW-1025-a-18-1-o"))
        >>> question = exam.questions[0]
        >>> record = await process_question(
        ...     question=question,
        ...     exam=exam,
        ...     model=OpenAIModel.GPT_4O,
        ... )
        >>> record.question_number
        '1'
        >>> record.page_images
        ['q01/pages/page1.png', 'q01/pages/page2.png']
    """
    # Extract question number from directory name (q01 -> "1")
    question_number = question.get_question_number()
    
    # Transcribe the question using OCR agent
    logger.info(
        "Transcribing question={question} images={n}",
        question=question.number,
        n=len(question.pages) + len(question.figures),
    )
    
    ocr = await transcribe_question_images(
        page_images=question.pages,
        figure_images=question.figures,
        model=model,
    )
    
    # Build question record with relative paths
    relative_paths = question.paths_relative_to(exam.exam_dir)
    
    return QuestionRecord(
        id=f"{exam.name}-q{question_number}",
        exam=exam.exam,
        question_number=str(question_number),
        question_text=ocr.question_text,
        figure=ocr.figure,
        source_images=relative_paths['all'],
        page_images=relative_paths['pages'],
        figure_images=relative_paths['figures'],
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

    # Validate and load exam structure
    exam = ExamFolderStructure.from_exam_dir(exam_dir)
    logger.info("Found {n} questions", n=len(exam.questions))
    
    # Process each question with progress bar
    with create_progress_bar(f"Processing {exam.name}", total=len(exam.questions)) as (progress, task):
        with out_path.open("w", encoding="utf-8") as f:
            for question in exam.questions:
                try:
                    record = await process_question(
                        question=question,
                        exam=exam,
                        model=model,
                    )
                    f.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False) + "\n")
                    progress.update(task, advance=1, description=f"✓ {exam.name} - q{record.question_number}")
                except ValueError as e:
                    logger.warning("Skipping {question}: {error}", question=question.number, error=e)
                    progress.update(task, advance=1, description=f"⚠ {exam.name} - {question.number} (skipped)")
                    continue


def process_exam(*, exam_dir: Path, out_path: Path, model: OpenAIModel) -> None:
    """
    CLI entry point: Process exam directory synchronously.
    
    Args:
        exam_dir: Path to exam directory
        out_path: Output JSONL path
        model: OpenAI model to use
    """
    asyncio.run(process_exam_dir(exam_dir=exam_dir, out_path=out_path, model=model))
