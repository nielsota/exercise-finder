from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode # type: ignore[import-not-found]

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


def questions_extracted_exam_dir(exam_id: str) -> Path:
    """
    Directory containing extracted QuestionRecord YAML files for a single exam.
    
    Example:
        questions_extracted_exam_dir("VW-1025-a-19-1-o")
        -> data/questions-extracted/VW-1025-a-19-1-o/
    """
    return questions_extracted_dir() / exam_id


def questions_extracted_yaml(exam_id: str) -> Path:
    """
    DEPRECATED: Use questions_extracted_exam_dir() instead.
    
    Path to the extracted QuestionRecord YAML for an exam.
    This function is kept for backwards compatibility but the new structure
    uses individual q<N>.yaml files within an exam directory.
    """
    return questions_extracted_dir() / f"{exam_id}.yaml"


def questions_formatted_dir() -> Path:
    return data_dir() / QUESTIONS_FORMATTED_DIRNAME


def formatted_exam_dir(exam_id: str) -> Path:
    """
    Directory containing pre-formatted multipart questions for a single exam.
    
    Example:
        formatted_exam_dir("VW-1025-a-19-1-o")
        -> data/questions-formatted/exams/VW-1025-a-19-1-o/
    """
    return questions_formatted_dir() / "exams" / exam_id


def formatted_question_path(exam_id: str, question_number: str) -> Path:
    """
    Path to a pre-formatted multipart question YAML file.
    """
    return formatted_exam_dir(exam_id) / f"q{question_number}.yaml"


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


# Practice exercises paths
PRACTICE_EXERCISES_DIRNAME = "practice-exercises"


def practice_exercises_dir() -> Path:
    """Directory containing practice exercise topic directories."""
    return questions_formatted_dir() / PRACTICE_EXERCISES_DIRNAME


def practice_exercise_dir(topic: str) -> Path:
    """
    Path to a practice exercise topic directory.
    
    Example:
        practice_exercise_dir("unitcircle") 
        -> data/questions-formatted/practice-exercises/unitcircle/
    """
    return practice_exercises_dir() / topic


# ========================================
# Cognito URL Helpers
# ========================================

def cognito_login_url(domain: str, params: dict[str, str] | None = None) -> str:
    """
    Cognito hosted UI login endpoint with encoded query parameters.
    
    Args:
        domain: Cognito domain (e.g., 'mathwizard.auth.us-east-1.amazoncognito.com')
        params: Query parameters to encode (e.g., client_id, redirect_uri, scope)
    
    Returns:
        Full URL to Cognito login endpoint with query string
    
    Example:
        cognito_login_url(
            "mathwizard.auth.us-east-1.amazoncognito.com",
            {"client_id": "abc123", "response_type": "code"}
        )
        -> "https://mathwizard.auth.us-east-1.amazoncognito.com/login?client_id=abc123&response_type=code"
    """
    
    
    base_url = f"https://{domain}/login"
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url


def cognito_token_url(domain: str) -> str:
    """
    Cognito OAuth token endpoint.
    
    Args:
        domain: Cognito domain (e.g., 'mathwizard.auth.us-east-1.amazoncognito.com')
    
    Returns:
        Full URL to Cognito token endpoint
    
    Example:
        cognito_token_url("mathwizard.auth.us-east-1.amazoncognito.com")
        -> "https://mathwizard.auth.us-east-1.amazoncognito.com/oauth2/token"
    """
    return f"https://{domain}/oauth2/token"


def cognito_logout_url(domain: str, params: dict[str, str] | None = None) -> str:
    """
    Cognito hosted UI logout endpoint with encoded query parameters.
    
    Args:
        domain: Cognito domain (e.g., 'mathwizard.auth.us-east-1.amazoncognito.com')
        params: Query parameters to encode (e.g., client_id, logout_uri)
    
    Returns:
        Full URL to Cognito logout endpoint with query string
    
    Example:
        cognito_logout_url(
            "mathwizard.auth.us-east-1.amazoncognito.com",
            {"client_id": "abc123", "logout_uri": "https://example.com/login"}
        )
        -> "https://mathwizard.auth.us-east-1.amazoncognito.com/logout?client_id=abc123&logout_uri=..."
    """
    
    base_url = f"https://{domain}/logout"
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url
