"""Helper functions for extracting questions from image directories."""
from pathlib import Path
import re

from exercise_finder.constants import image_suffixes
from exercise_finder.pydantic_models import Exam

def _exam_from_exam_dir(exam_dir: Path) -> Exam:
    """
    Infer Exam metadata from an exam directory name like 'VW-1025-a-18-1-o'.
    Reuses Exam.from_file_path() parsing rules.

    Example:
    data/questions-images/VW-1025-a-18-1-o/
    |-- VW-1025-a-18-1-o.pdf
    return Exam(
        level=ExamLevel.VWO,
        year=2018,
        tijdvak=1,
    )
    """
    return Exam.from_file_path(Path(f"{exam_dir.name}.pdf"))


def _iter_question_dirs(exam_dir: Path) -> list[Path]:
    """
    Iterate over the question directories in an exam directory.

    Example:
    data/questions-images/VW-1025-a-18-1-o/
    |-- q1/
    |-- q2/
    return [Path("data/questions-images/VW-1025-a-18-1-o/q1"), Path("data/questions-images/VW-1025-a-18-1-o/q2")]
    """
    question_dirs = sorted(
        [p for p in exam_dir.iterdir() if p.is_dir() and re.fullmatch(r"q\d+", p.name.lower())],
        key=lambda p: p.name,
    )

    if not question_dirs:
        raise ValueError(f"No question directories found in {exam_dir}")

    return question_dirs

def _parse_question_number(dir_name: str) -> str:
    """
    Strict format: qNN -> "NN" (without leading zeros).
    """
    match = re.fullmatch(r"q(\d+)", dir_name.lower())
    if not match:
        raise ValueError(f"Question directory must match qNN, got: {dir_name}")
    return str(int(match.group(1)))


def _iter_images_in_dir(path: Path) -> list[Path]:
    """
    Iterate over the images in a directory.

    Expected structure (strict):
    question_dir/
      |-- pages/
      |   |-- page1.png
      |   |-- page2.png
      |-- figures/
      |   |-- figure1.png
      |   |-- figure2.png
    return [
        Path("question_dir/pages/page1.png"),
        Path("question_dir/pages/page2.png"),
        Path("question_dir/figures/figure1.png"),
        Path("question_dir/figures/figure2.png"),
    ]
    """
    if not path.exists() or not path.is_dir():
        return []
    images = [
        p
        for p in path.iterdir()
        if p.is_file()
        and p.suffix.lower() in image_suffixes
        and not p.name.startswith(".")
    ]
    return sorted(images, key=lambda p: p.name)


def get_pages_and_figures_from_question_dir(question_dir: Path) -> tuple[list[Path], list[Path]]:
    """
    Get the pages and figures from a question directory.

    Example:
    question_dir/
    |-- pages/
    |   |-- page1.png
    |   |-- page2.png
    |-- figures/
    |   |-- figure1.png
    |   |-- figure2.png
    return (
        [Path("question_dir/pages/page1.png"), Path("question_dir/pages/page2.png")],
        [Path("question_dir/figures/figure1.png"), Path("question_dir/figures/figure2.png")]
    )
    """
    pages = _iter_images_in_dir(question_dir / "pages")
    figures = _iter_images_in_dir(question_dir / "figures")

    if not pages:
        raise ValueError(f"No page images found in {question_dir / 'pages'}")

    return pages, figures


def paths_relative_to(paths: list[Path], base: Path) -> list[str]:
    """
    Convert absolute paths to relative paths (as strings) for serialization.
    
    Example:
        >>> base = Path("/data/exams/VW-1025-a-18-1-o")
        >>> paths = [
        ...     Path("/data/exams/VW-1025-a-18-1-o/q01/pages/page1.png"),
        ...     Path("/data/exams/VW-1025-a-18-1-o/q01/figures/fig1.png"),
        ... ]
        >>> paths_relative_to(paths, base)
        ['q01/pages/page1.png', 'q01/figures/fig1.png']
    """
    return [str(p.relative_to(base)) for p in paths]