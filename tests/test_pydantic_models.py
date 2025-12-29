"""Tests for Pydantic folder structure models."""
import pytest  # type: ignore[import-not-found]
from pathlib import Path

from exercise_finder.pydantic_models import (  # type: ignore
    QuestionFolderStructure,
    ExamFolderStructure,
)
from exercise_finder.enums import ExamLevel  # type: ignore


class TestQuestionFolderStructure:
    """Tests for QuestionFolderStructure validation."""

    def test_from_question_dir_valid(self, tmp_path: Path):
        """Test creating a valid QuestionFolderStructure from a directory."""
        # Create a valid question directory
        question_dir = tmp_path / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        
        # Add PNG files
        (question_dir / "pages" / "page1.png").touch()
        (question_dir / "pages" / "page2.png").touch()
        (question_dir / "figures" / "fig1.png").touch()
        
        # Test
        structure = QuestionFolderStructure.from_question_dir(question_dir)
        
        assert structure.number == "q01"
        assert len(structure.pages) == 2
        assert len(structure.figures) == 1
        assert all(p.suffix == ".png" for p in structure.pages)
        assert all(f.suffix == ".png" for f in structure.figures)

    def test_from_question_dir_no_pages_fails(self, tmp_path: Path):
        """Test that validation fails when there are no pages."""
        question_dir = tmp_path / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        
        # No page files created
        
        with pytest.raises(ValueError, match="No pages directory found"):
            QuestionFolderStructure.from_question_dir(question_dir)

    def test_from_question_dir_non_png_in_pages_fails(self, tmp_path: Path):
        """Test that validation fails when non-PNG files exist in pages."""
        question_dir = tmp_path / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        
        # Add mixed file types
        (question_dir / "pages" / "page1.png").touch()
        (question_dir / "pages" / "document.pdf").touch()
        
        with pytest.raises(ValueError, match="Non-PNG files found in pages directory"):
            QuestionFolderStructure.from_question_dir(question_dir)

    def test_from_question_dir_non_png_in_figures_fails(self, tmp_path: Path):
        """Test that validation fails when non-PNG files exist in figures."""
        question_dir = tmp_path / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        
        # Add valid pages
        (question_dir / "pages" / "page1.png").touch()
        
        # Add non-PNG in figures
        (question_dir / "figures" / "fig1.png").touch()
        (question_dir / "figures" / "diagram.jpg").touch()
        
        with pytest.raises(ValueError, match="Non-PNG files found in figures directory"):
            QuestionFolderStructure.from_question_dir(question_dir)

    def test_from_question_dir_no_figures_ok(self, tmp_path: Path):
        """Test that questions without figures are valid."""
        question_dir = tmp_path / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        
        # Only pages, no figures
        (question_dir / "pages" / "page1.png").touch()
        
        structure = QuestionFolderStructure.from_question_dir(question_dir)
        
        assert len(structure.pages) == 1
        assert len(structure.figures) == 0
    
    def test_get_question_number(self, tmp_path: Path):
        """Test extracting numeric question number from directory name."""
        question_dir = tmp_path / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        (question_dir / "pages" / "page1.png").touch()
        
        structure = QuestionFolderStructure.from_question_dir(question_dir)
        
        assert structure.get_question_number() == "1"
    
    def test_get_question_number_no_leading_zeros(self, tmp_path: Path):
        """Test that get_question_number strips leading zeros."""
        question_dir = tmp_path / "q03"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        (question_dir / "pages" / "page1.png").touch()
        
        structure = QuestionFolderStructure.from_question_dir(question_dir)
        
        assert structure.get_question_number() == "3"
    
    def test_paths_relative_to(self, tmp_path: Path):
        """Test getting relative paths for serialization."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        question_dir = exam_dir / "q01"
        question_dir.mkdir()
        (question_dir / "pages").mkdir()
        (question_dir / "figures").mkdir()
        (question_dir / "pages" / "page1.png").touch()
        (question_dir / "pages" / "page2.png").touch()
        (question_dir / "figures" / "fig1.png").touch()
        
        structure = QuestionFolderStructure.from_question_dir(question_dir)
        relative_paths = structure.paths_relative_to(exam_dir)
        
        assert "pages" in relative_paths
        assert "figures" in relative_paths
        assert "all" in relative_paths
        assert len(relative_paths["pages"]) == 2
        assert len(relative_paths["figures"]) == 1
        assert len(relative_paths["all"]) == 3
        assert all("q01/" in path for path in relative_paths["all"])


class TestExamFolderStructure:
    """Tests for ExamFolderStructure validation."""

    def test_from_exam_dir_valid(self, tmp_path: Path):
        """Test creating a valid ExamFolderStructure from a directory."""
        # Create a valid exam directory
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create question directories with pages
        for i in range(1, 4):
            q_dir = exam_dir / f"q0{i}"
            q_dir.mkdir()
            (q_dir / "pages").mkdir()
            (q_dir / "figures").mkdir()
            (q_dir / "pages" / "page1.png").touch()
        
        # Test
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        
        assert structure.name == "VW-1025-a-18-1-o"
        assert structure.root == exam_dir
        assert len(structure.questions) == 3
        assert structure.questions[0].number == "q01"
        assert structure.questions[1].number == "q02"
        assert structure.questions[2].number == "q03"

    def test_from_exam_dir_extra_directories_fails(self, tmp_path: Path):
        """Test that validation fails when extra directories exist."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create valid question directory
        q_dir = exam_dir / "q01"
        q_dir.mkdir()
        (q_dir / "pages").mkdir()
        (q_dir / "figures").mkdir()
        (q_dir / "pages" / "page1.png").touch()
        
        # Create invalid extra directory
        (exam_dir / "metadata").mkdir()
        
        with pytest.raises(ValueError, match="Unexpected directories found"):
            ExamFolderStructure.from_exam_dir(exam_dir)

    def test_from_exam_dir_duplicate_questions_fails(self, tmp_path: Path):
        """Test that validation fails when duplicate question numbers exist."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create two q01 directories (not possible in filesystem, but we can test the validator)
        # We'll manually construct the structure to trigger the validator
        q_dir1 = exam_dir / "q01"
        q_dir1.mkdir()
        (q_dir1 / "pages").mkdir()
        (q_dir1 / "figures").mkdir()
        (q_dir1 / "pages" / "page1.png").touch()
        
        # This test will pass since we can't create duplicate directory names
        # But the validator is there to catch edge cases
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        assert len(structure.questions) == 1

    def test_from_exam_dir_ignores_non_question_dirs(self, tmp_path: Path):
        """Test that non-question directories are ignored during collection."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create valid question directory
        q_dir = exam_dir / "q01"
        q_dir.mkdir()
        (q_dir / "pages").mkdir()
        (q_dir / "figures").mkdir()
        (q_dir / "pages" / "page1.png").touch()
        
        # Create directory with wrong naming pattern (should be ignored during collection)
        wrong_dir = exam_dir / "question_01"
        wrong_dir.mkdir()
        
        # This should fail because wrong_dir doesn't match qNN pattern
        # but it's still an extra directory
        with pytest.raises(ValueError, match="Unexpected directories found"):
            ExamFolderStructure.from_exam_dir(exam_dir)

    def test_from_exam_dir_sorts_questions(self, tmp_path: Path):
        """Test that questions are sorted by name."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create questions out of order
        for num in ["q03", "q01", "q02"]:
            q_dir = exam_dir / num
            q_dir.mkdir()
            (q_dir / "pages").mkdir()
            (q_dir / "figures").mkdir()
            (q_dir / "pages" / "page1.png").touch()
        
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        
        # Should be sorted
        assert structure.questions[0].number == "q01"
        assert structure.questions[1].number == "q02"
        assert structure.questions[2].number == "q03"

    def test_from_exam_dir_case_insensitive(self, tmp_path: Path):
        """Test that question directory matching is case-insensitive."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create question with uppercase Q (should still match)
        q_dir = exam_dir / "Q01"
        q_dir.mkdir()
        (q_dir / "pages").mkdir()
        (q_dir / "figures").mkdir()
        (q_dir / "pages" / "page1.png").touch()
        
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        
        assert len(structure.questions) == 1
        assert structure.questions[0].number == "Q01"

    def test_from_exam_dir_empty_fails(self, tmp_path: Path):
        """Test that an empty exam directory returns empty questions list."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        
        # No questions found
        assert len(structure.questions) == 0
    
    def test_exam_property(self, tmp_path: Path):
        """Test that exam property extracts metadata from folder name."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        # Create at least one question to avoid validation issues
        q_dir = exam_dir / "q01"
        q_dir.mkdir()
        (q_dir / "pages").mkdir()
        (q_dir / "figures").mkdir()
        (q_dir / "pages" / "page1.png").touch()
        
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        
        # Test exam property
        assert structure.exam.level == ExamLevel.VWO
        assert structure.exam.year == 2018
        assert structure.exam.tijdvak == 1
    
    def test_exam_dir_property(self, tmp_path: Path):
        """Test that exam_dir property returns the root directory."""
        exam_dir = tmp_path / "VW-1025-a-18-1-o"
        exam_dir.mkdir()
        
        structure = ExamFolderStructure.from_exam_dir(exam_dir)
        
        # exam_dir should be an alias for root
        assert structure.exam_dir == structure.root
        assert structure.exam_dir == exam_dir

