from __future__ import annotations

from pathlib import Path
from typing import Callable
import asyncio
import yaml  # type: ignore[import-untyped]

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
    1. Load the question records from exam directories (one YAML file per question).
    2. Format each question record using the specialized agent (one formatted question per question record).
    3. Save each formatted question to a file in the output directory (one YAML file per question record).
    """
    # Find all exam directories (each contains multiple YAML files)
    exam_dirs = sorted([d for d in question_records_dir.iterdir() if d.is_dir()])
    
    if not exam_dirs:
        raise ValueError(f"No exam directories found in {question_records_dir}")
    
    # Calculate total questions for progress bar
    exam_data = []
    total_questions = 0
    for exam_dir in exam_dirs:
        try:
            question_records = QuestionRecord.from_exam_dir(exam_dir)
            total_questions += len(question_records)
            exam_data.append((exam_dir.name, question_records))
        except ValueError:
            # Skip directories without valid YAML files
            continue
    
    # Process all questions with progress bar
    with create_progress_bar("Formatting questions", total=total_questions) as (progress, task):
        for exam_id, question_records in exam_data:
            # Create the exam output directory
            exam_out_dir = out_dir / exam_id
            exam_out_dir.mkdir(parents=True, exist_ok=True)

            for question_record in question_records:
                try:
                    # LLM agent formats the question text (returns AgentMultipartQuestionOutput)
                    agent_output = asyncio.run(
                        format_multipart_question(
                            question_text=question_record.question_text,
                            model=model
                        )
                    )
                    
                    # Promote to MultipartQuestionOutput and add metadata
                    formatted_question = MultipartQuestionOutput(
                        # Agent output (text content)
                        title=agent_output.title,
                        stem=agent_output.stem,
                        parts=agent_output.parts,
                        
                        # Metadata from QuestionRecord (NOT agent-generated)
                        exam_id=question_record.exam.id,
                        page_images=question_record.page_images or [],
                        figure_images=question_record.figure_images or [],
                        calculator_allowed=None,  # Not in QuestionRecord currently
                    )

                    # Save as YAML (not JSON)
                    question_number = question_record.question_number
                    out_path = exam_out_dir / f"q{question_number}.yaml"
                    with open(out_path, "w") as f:
                        yaml.dump(
                            formatted_question.model_dump(mode="json"),
                            f,
                            allow_unicode=True,
                            default_flow_style=False
                        )
                    
                    progress.update(task, advance=1, description=f"✓ {exam_id} - q{question_number}")
                except Exception:
                    progress.update(task, advance=1, description=f"⚠ {exam_id} - q{question_record.question_number} (failed)")


def load_formatted_question_from_exam_and_question_number(
    *,
    exam_id: str,
    question_number: str,
    quesion_path: Callable[[str, str], Path] = paths.formatted_question_path,
) -> MultipartQuestionOutput:
    """
    Load a formatted question from a YAML file in the output directory.
    """
    out_path = quesion_path(exam_id, question_number)

    if not out_path.exists():
        raise FileNotFoundError(f"Formatted question file not found: {out_path}")
    
    # load the formatted question from the file
    return load_formatted_question(formatted_question_path=out_path)


def load_formatted_question(
    *,
    formatted_question_path: Path,
) -> MultipartQuestionOutput:
    """
    Load a formatted question from a YAML file.
    """
    with open(formatted_question_path, "r") as f:
        data = yaml.safe_load(f)
        return MultipartQuestionOutput.model_validate(data)
