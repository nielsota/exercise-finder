from pathlib import Path

from exercise_finder.pydantic_models import Exam # type: ignore
from exercise_finder.enums import ExamLevel # type: ignore
from exercise_finder.services.image_to_question.helpers import ( # type: ignore
    _exam_from_exam_dir,
    _iter_question_dirs,
    _parse_question_number,
    _iter_images_in_dir,
    get_pages_and_figures_from_question_dir,
) # type: ignore

def test_exam_from_exam_dir():
    exam_dir = Path("data/questions-images/VW-1025-a-18-1-o")
    exam = _exam_from_exam_dir(exam_dir)
    assert exam == Exam(
        level=ExamLevel.VWO,
        year=2018,
        tijdvak=1,
    )


def test_iter_question_dirs(tmp_path: Path):
    """Test that _iter_question_dirs returns question directories."""
    # Create a fake exam directory structure
    exam_dir = tmp_path / "VW-1025-a-18-1-o"
    exam_dir.mkdir()
    
    # Create question directories
    (exam_dir / "q01").mkdir()
    (exam_dir / "q02").mkdir()
    (exam_dir / "q03").mkdir()
    
    # Create some non-question files/dirs (should be ignored)
    (exam_dir / "metadata.json").touch()
    (exam_dir / "images").mkdir()
    
    # Test
    question_dirs = list(_iter_question_dirs(exam_dir))
    
    assert len(question_dirs) == 3
    assert all(d.name.startswith("q") for d in question_dirs)
    assert (exam_dir / "q01") in question_dirs


def test_parse_question_number():
    """Test that _parse_question_number returns the correct question number."""
    assert _parse_question_number("q01") == "1"
    assert _parse_question_number("q02") == "2"
    assert _parse_question_number("q03") == "3"


def test_iter_images_in_dir(tmp_path: Path):
    """Test that _iter_images_in_dir returns images in the correct directory."""
    # Create a fake question directory structure
    question_dir = tmp_path / "q01"
    question_dir.mkdir()
    
    # Create some images
    (question_dir / "page1.png").touch()
    (question_dir / "page2.png").touch()
    (question_dir / "figure1.png").touch()
    (question_dir / "figure2.png").touch()
    (question_dir / "wrong_format.fake_extension").touch()

    # Test
    images = _iter_images_in_dir(question_dir)
    assert len(images) == 4
    assert all(i.name.endswith(".png") for i in images)
    assert (question_dir / "page1.png") in images
    assert (question_dir / "page2.png") in images
    assert (question_dir / "figure1.png") in images
    assert (question_dir / "figure2.png") in images
    assert (question_dir / "wrong_format.fake_extension") not in images


def test_get_pages_and_figures_from_question_dir(tmp_path: Path):
    """Test that get_pages_and_figures_from_question_dir returns the correct pages and figures."""
    # Create a fake question directory structure
    question_dir = tmp_path / "q01"
    question_dir.mkdir()
    (question_dir / "pages").mkdir()
    (question_dir / "figures").mkdir()
    
    # Create some images
    (question_dir / "pages" / "page1.png").touch()
    (question_dir / "pages" / "page2.png").touch()
    (question_dir / "figures" / "figure1.png").touch()
    (question_dir / "figures" / "figure2.png").touch()

    # Test
    pages, figures = get_pages_and_figures_from_question_dir(question_dir)
    assert len(pages) == 2
    assert len(figures) == 2
    assert (question_dir / "pages" / "page1.png") in pages
    assert (question_dir / "pages" / "page2.png") in pages
    assert (question_dir / "figures" / "figure1.png") in figures
    assert (question_dir / "figures" / "figure2.png") in figures