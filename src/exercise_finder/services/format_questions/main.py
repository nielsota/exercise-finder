from __future__ import annotations

from pathlib import Path
import asyncio

from exercise_finder.enums import OpenAIModel
from exercise_finder.services.format_questions.helpers import _format_question, _save_formatted_question
from exercise_finder.pydantic_models import MultipartQuestionOutput, QuestionRecord
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
    for exam_json in question_records_dir.glob("*.jsonl"):

        # create the exam output directory
        exam_id = exam_json.stem
        exam_out_dir = out_dir / exam_id
        exam_out_dir.mkdir(parents=True, exist_ok=True)

        # load the question records from the input directory
        question_records: list[QuestionRecord] = QuestionRecord.from_jsonl(exam_json)

        for question_record in question_records:

            # format the question text
            formatted_question = asyncio.run(_format_question(question_text=question_record.question_text, model=model))

            # save the formatted question to a file
            question_number = question_record.question_number
            out_path = exam_out_dir / f"q{question_number}.json"
            _save_formatted_question(
                formatted_question=formatted_question,
                out_path=out_path,
            )


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
