"""Tests for exam processing - now using Pydantic models directly."""
from pathlib import Path

from exercise_finder.pydantic_models import (  # type: ignore
    ExamFolderStructure,
    QuestionFolderStructure,
)
from exercise_finder.enums import ExamLevel  # type: ignore


def test_exam_from_exam_dir(tmp_path: Path):
    """Test extracting exam metadata from directory name."""
    # Create a valid exam directory structure
    exam_dir = tmp_path / "VW-1025-a-18-1-o"
    exam_dir.mkdir()
    
    # Add at least one valid question
    q_dir = exam_dir / "q01"
    q_dir.mkdir()
    (q_dir / "pages").mkdir()
    (q_dir / "figures").mkdir()
    (q_dir / "pages" / "page1.png").touch()
    
    exam_structure = ExamFolderStructure.from_exam_dir(exam_dir)
    
    # Test exam property extracts metadata correctly
    assert exam_structure.exam.level == ExamLevel.VWO
    assert exam_structure.exam.year == 2018
    assert exam_structure.exam.tijdvak == 1


def test_parse_question_number(tmp_path: Path):
    """Test extracting question number from directory name."""
    # Create test directories
    for q_num in ["q01", "q02", "q03"]:
        q_dir = tmp_path / q_num
        q_dir.mkdir()
        (q_dir / "pages").mkdir()
        (q_dir / "figures").mkdir()
        (q_dir / "pages" / "page1.png").touch()
    
    # Test question number extraction
    q1 = QuestionFolderStructure.from_question_dir(tmp_path / "q01")
    q2 = QuestionFolderStructure.from_question_dir(tmp_path / "q02")
    q3 = QuestionFolderStructure.from_question_dir(tmp_path / "q03")
    
    assert q1.get_question_number() == "1"
    assert q2.get_question_number() == "2"
    assert q3.get_question_number() == "3"


def test_question_structure_loads_images(tmp_path: Path):
    """Test that QuestionFolderStructure loads PNG images correctly."""
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
    structure = QuestionFolderStructure.from_question_dir(question_dir)
    
    assert len(structure.pages) == 2
    assert len(structure.figures) == 2
    assert (question_dir / "pages" / "page1.png") in structure.pages
    assert (question_dir / "pages" / "page2.png") in structure.pages
    assert (question_dir / "figures" / "figure1.png") in structure.figures
    assert (question_dir / "figures" / "figure2.png") in structure.figures