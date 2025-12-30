from __future__ import annotations

from pathlib import Path
import asyncio
import json

from exercise_finder.enums import OpenAIModel
from exercise_finder.agents.format_multipart import format_multipart_question
from exercise_finder.pydantic_models import MultipartQuestionOutput, QuestionRecord
from exercise_finder.utils.progressbar import create_progress_bar
import exercise_finder.paths as paths

## MAIN FUNCTION ##

def format_questions(
    question_records_dir: Path,
    out_dir: Path = paths.questions_formatted_dir(),
    model: OpenAIModel = OpenAIModel.GPT_5_MINI,
) -> None:
    """
    Format a directory of question records into a directory of formatted questions
    using a specialized agent.

    Side effects:
    - Saves each formatted question to a file in the output directory.

    Steps:
    1. Load the question records from the input directory (one JSONL file per exam).
    2. Format each question record using the specialized agent (one formatted question per question record).
    3. Save each formatted question to a file in the output directory (one JSON file per question record).
    """
    # Collect all JSONL files and count total questions
    jsonl_files = list(question_records_dir.glob("*.jsonl"))
    
    if not jsonl_files:
        return
    
    # Calculate total questions for progress bar
    exam_data = []
    total_questions = 0
    for exam_json in jsonl_files:
        question_records = QuestionRecord.from_jsonl(exam_json)
        total_questions += len(question_records)
        exam_data.append((exam_json, question_records))
    
    # Process all questions with progress bar
    with create_progress_bar("Formatting questions", total=total_questions) as (progress, task):
        for exam_json, question_records in exam_data:
            # Create the exam output directory
            exam_id = exam_json.stem
            exam_out_dir = out_dir / exam_id
            exam_out_dir.mkdir(parents=True, exist_ok=True)

            for question_record in question_records:
                try:
                    # Format the question text
                    formatted_question = asyncio.run(
                        format_multipart_question(
                            question_text=question_record.question_text,
                            model=model
                        )
                    )

                    # Save the formatted question to a file
                    question_number = question_record.question_number
                    out_path = exam_out_dir / f"q{question_number}.json"
                    with open(out_path, "w") as f:
                        json.dump(formatted_question.model_dump(mode="json"), f)
                    
                    progress.update(task, advance=1, description=f"✓ {exam_id} - q{question_number}")
                except Exception:
                    progress.update(task, advance=1, description=f"⚠ {exam_id} - q{question_record.question_number} (failed)")


def load_formatted_question_from_exam_and_question_number(
    *,
    exam_id: str,
    question_number: str,
    out_dir: Path = paths.questions_formatted_dir(),
) -> MultipartQuestionOutput:
    """
    Load a formatted question from a file in the output directory.
    """
    out_path = out_dir / exam_id / f"q{question_number}.json"

    if not out_path.exists():
        raise FileNotFoundError(f"Formatted question file not found: {out_path}")
    
    # load the formatted question from the file
    return load_formatted_question(formatted_question_path=out_path)


def load_formatted_question(
    *,
    formatted_question_path: Path,
) -> MultipartQuestionOutput:
    """
    Load a formatted question from a file.
    """
    with open(formatted_question_path, "r") as f:
        return MultipartQuestionOutput.model_validate_json(f.read())
