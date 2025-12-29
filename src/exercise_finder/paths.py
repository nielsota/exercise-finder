from __future__ import annotations

from pathlib import Path

"""
Centralized path helpers/constants for this repo.
"""


# Relative directory names (under repo root)
DATA_DIRNAME = "data"
QUESTIONS_IMAGES_DIRNAME = "questions-images"
QUESTIONS_EXTRACTED_DIRNAME = "questions-extracted"
QUESTIONS_FORMATTED_DIRNAME = "questions-formatted"
VECTORSTORE_INDEX_DIRNAME = "vectorstore-index"

PAGES_DIRNAME = "pages"
FIGURES_DIRNAME = "figures"


def repo_root() -> Path:
    """
    Return the repository root directory.

    Assumes this file lives at: <repo>/src/exercise_finder/paths.py
    """
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return repo_root() / DATA_DIRNAME


def questions_images_root() -> Path:
    return data_dir() / QUESTIONS_IMAGES_DIRNAME


def exam_images_dir(exam_id: str) -> Path:
    """
    Directory containing images for a single exam.
    """
    return questions_images_root() / exam_id


def exam_asset_path(exam_id: str, rel_path: str | Path) -> Path:
    """
    Resolve a record-relative path like `q03/pages/page4.png` under an exam directory.
    """
    return exam_images_dir(exam_id) / rel_path


def exam_asset_under_root(exams_root: Path, exam_id: str, rel_path: str | Path) -> Path:
    """
    Resolve a record-relative path like `q03/pages/page4.png` under a provided exams root.

    `exams_root` should be the folder that contains multiple exam folders (e.g. `data/questions-images`).
    """
    return exams_root / exam_id / rel_path


def question_dirname(question_number: str | int) -> str:
    """
    Convert a question number into the `qNN` directory name used on disk.
    """
    if isinstance(question_number, int):
        return f"q{question_number:02d}"
    return f"q{question_number}"


def question_pages_dir(exam_id: str, question_number: str | int) -> Path:
    """
    Directory containing page images for a single question.
    """
    return exam_images_dir(exam_id) / question_dirname(question_number) / PAGES_DIRNAME


def question_figures_dir(exam_id: str, question_number: str | int) -> Path:
    """
    Directory containing figure images for a single question.
    """
    return exam_images_dir(exam_id) / question_dirname(question_number) / FIGURES_DIRNAME


def page_image_path(exam_id: str, question_number: str | int, filename: str) -> Path:
    """
    Path to a single page image (e.g. `page4.png`) for a question.
    """
    return question_pages_dir(exam_id, question_number) / filename


def figure_image_path(exam_id: str, question_number: str | int, filename: str) -> Path:
    """
    Path to a single figure image (e.g. `fig1.png`) for a question.
    """
    return question_figures_dir(exam_id, question_number) / filename


def questions_extracted_dir() -> Path:
    return data_dir() / QUESTIONS_EXTRACTED_DIRNAME


def questions_extracted_jsonl(exam_id: str) -> Path:
    """
    Path to the extracted QuestionRecord JSONL for an exam.
    """
    return questions_extracted_dir() / f"{exam_id}.jsonl"


def questions_formatted_dir() -> Path:
    return data_dir() / QUESTIONS_FORMATTED_DIRNAME


def formatted_exam_dir(exam_id: str) -> Path:
    """
    Directory containing pre-formatted multipart questions for a single exam.
    """
    return questions_formatted_dir() / exam_id


def formatted_question_path(exam_id: str, question_number: str) -> Path:
    """
    Path to a pre-formatted multipart question JSON file.
    """
    return formatted_exam_dir(exam_id) / f"q{question_number}.json"


def vectorstore_index_dir() -> Path:
    return data_dir() / VECTORSTORE_INDEX_DIRNAME


def vectorstore_dataset_dir(dataset_name: str) -> Path:
    """
    Local directory where we materialize per-question index .txt files before upload.
    """
    return vectorstore_index_dir() / dataset_name


def vectorstore_index_file_path(dataset_name: str, record_id: str) -> Path:
    """
    Path to a single per-question index .txt file (before upload).
    """
    return vectorstore_dataset_dir(dataset_name) / f"{record_id}.txt"
