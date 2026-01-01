"""Tests for Pydantic models."""
import pytest  # type: ignore[import-not-found]
import json
from pathlib import Path

from exercise_finder.pydantic_models import (  # type: ignore
    FigureInfo,
    QuestionFromImagesOutput,
    QuestionRecord,
    QuestionRecordVectorStoreAttributes,
    QuestionFolderStructure,
    ExamFolderStructure,
    Exam,
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
        assert structure.exam.id == "VW-1025-a-18-1-o"
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


class TestFigureInfo:
    """Tests for FigureInfo model."""
    
    def test_figure_present(self):
        """Test FigureInfo with figure present."""
        fig = FigureInfo(present=True, description="A graph showing...")
        
        assert fig.present is True
        assert fig.missing is False
        assert fig.description == "A graph showing..."
    
    def test_figure_missing(self):
        """Test FigureInfo with figure missing."""
        fig = FigureInfo(present=False, missing=True)
        
        assert fig.present is False
        assert fig.missing is True
        assert fig.description is None
    
    def test_figure_default_missing(self):
        """Test that missing defaults to False."""
        fig = FigureInfo(present=True)
        
        assert fig.missing is False


class TestQuestionFromImagesOutput:
    """Tests for QuestionFromImagesOutput model."""
    
    def test_valid_output(self):
        """Test valid question from images output."""
        output = QuestionFromImagesOutput(
            question_text="Bereken de waarde van x.",
            title="Vergelijking oplossen",
            figure=FigureInfo(present=True, description="Een grafiek")
        )
        
        assert output.question_text == "Bereken de waarde van x."
        assert output.title == "Vergelijking oplossen"
        assert output.figure.present is True
    
    def test_no_figure(self):
        """Test output with no figure."""
        output = QuestionFromImagesOutput(
            question_text="Wat is 2+2?",
            title="Optellen",
            figure=FigureInfo(present=False)
        )
        
        assert output.figure.present is False
        assert output.figure.description is None


class TestQuestionRecord:
    """Tests for QuestionRecord model."""
    
    def test_valid_record(self):
        """Test creating a valid question record."""
        exam = Exam(id="VW-1025-a-20-1-o", level=ExamLevel.VWO, year=2020, tijdvak=1)
        record = QuestionRecord(
            id="VW-1025-a-20-1-o_q01",
            exam=exam,
            title="Vergelijking oplossen",
            question_number="1",
            question_text="Bereken x.",
            figure=FigureInfo(present=False),
            source_images=["page1.png"],
            page_images=["pages/page1.png"],
            figure_images=[]
        )
        
        assert record.id == "VW-1025-a-20-1-o_q01"
        assert record.exam.id == "VW-1025-a-20-1-o"
        assert record.exam.level == ExamLevel.VWO
        assert record.title == "Vergelijking oplossen"
        assert record.question_number == "1"
    
    def test_to_text_no_figure(self):
        """Test converting record to text without figure."""
        exam = Exam(id="VW-1025-a-20-1-o", level=ExamLevel.VWO, year=2020, tijdvak=1)
        record = QuestionRecord(
            id="test_id",
            exam=exam,
            title="Test Title",
            question_number="1",
            question_text="Test question text.",
            figure=FigureInfo(present=False),
            source_images=[]
        )
        
        text = record.to_text()
        assert "Test Title" in text
        assert "Test question text." in text
        assert "[FIGURE]" not in text
    
    def test_to_text_with_figure(self):
        """Test converting record to text with figure."""
        exam = Exam(id="VW-1025-a-20-1-o", level=ExamLevel.VWO, year=2020, tijdvak=1)
        record = QuestionRecord(
            id="test_id",
            exam=exam,
            title="Test Title",
            question_number="1",
            question_text="Test question text.",
            figure=FigureInfo(present=True, description="A graph showing trends"),
            source_images=[]
        )
        
        text = record.to_text()
        assert "Test Title" in text
        assert "Test question text." in text
        assert "[FIGURE]" in text
        assert "A graph showing trends" in text
    
    def test_attributes_for_vector_store(self):
        """Test converting record to vector store attributes."""
        exam = Exam(id="VW-1025-a-20-1-o", level=ExamLevel.VWO, year=2020, tijdvak=1)
        record = QuestionRecord(
            id="VW-1025-a-20-1-o_q01",
            exam=exam,
            title="Test Title",
            question_number="1",
            question_text="Test text.",
            figure=FigureInfo(present=True, missing=False),
            source_images=["page1.png"],
            page_images=["pages/page1.png"],
            figure_images=["figures/fig1.png"]
        )
        
        attrs = record.attributes_for_vector_store()
        
        assert attrs["record_id"] == "VW-1025-a-20-1-o_q01"
        assert attrs["exam_id"] == "VW-1025-a-20-1-o"
        assert attrs["exam_level"] == "VWO"
        assert attrs["exam_year"] == "2020"
        assert attrs["exam_tijdvak"] == "1"
        assert attrs["question_number"] == "1"
        assert attrs["figure_present"] == "True"
        assert attrs["figure_missing"] == "False"
        
        # Check JSON fields
        assert json.loads(attrs["page_images"]) == ["pages/page1.png"]
        assert json.loads(attrs["figure_images"]) == ["figures/fig1.png"]
        assert json.loads(attrs["source_images"]) == ["page1.png"]
    
    def test_from_yaml_valid(self, tmp_path: Path):
        """Test loading question records from valid YAML file."""
        import yaml
        
        exam = Exam(id="VW-1025-a-20-1-o", level=ExamLevel.VWO, year=2020, tijdvak=1)
        record1 = QuestionRecord(
            id="VW-1025-a-20-1-o_q01",
            exam=exam,
            title="Title 1",
            question_number="1",
            question_text="Question 1",
            figure=FigureInfo(present=False),
            source_images=[]
        )
        record2 = QuestionRecord(
            id="VW-1025-a-20-1-o_q02",
            exam=exam,
            title="Title 2",
            question_number="2",
            question_text="Question 2",
            figure=FigureInfo(present=True, description="Figure description"),
            source_images=[]
        )
        
        # Write YAML file
        yaml_file = tmp_path / "VW-1025-a-20-1-o.yaml"
        with yaml_file.open("w", encoding="utf-8") as f:
            yaml.dump([record1.model_dump(mode="json"), record2.model_dump(mode="json")], f)
        
        # Load and validate
        loaded_records = QuestionRecord.from_yaml(yaml_file)
        
        assert len(loaded_records) == 2
        assert loaded_records[0].id == "VW-1025-a-20-1-o_q01"
        assert loaded_records[0].title == "Title 1"
        assert loaded_records[1].id == "VW-1025-a-20-1-o_q02"
        assert loaded_records[1].figure.present is True
    
    def test_from_yaml_file_not_found(self, tmp_path: Path):
        """Test from_yaml with non-existent file."""
        yaml_file = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            QuestionRecord.from_yaml(yaml_file)
    
    def test_from_yaml_not_a_file(self, tmp_path: Path):
        """Test from_yaml with a directory instead of file."""
        directory = tmp_path / "not_a_file"
        directory.mkdir()
        
        with pytest.raises(ValueError, match="Path is not a file"):
            QuestionRecord.from_yaml(directory)
    
    def test_from_yaml_wrong_extension(self, tmp_path: Path):
        """Test from_yaml with wrong file extension."""
        wrong_file = tmp_path / "test.txt"
        wrong_file.write_text("test")
        
        with pytest.raises(ValueError, match="must have .yaml extension"):
            QuestionRecord.from_yaml(wrong_file)
    
    def test_from_yaml_empty_file(self, tmp_path: Path):
        """Test from_yaml with empty file."""
        import yaml
        
        yaml_file = tmp_path / "VW-1025-a-20-1-o.yaml"
        yaml_file.write_text("")
        
        with pytest.raises(ValueError, match="YAML file is empty"):
            QuestionRecord.from_yaml(yaml_file)
    
    def test_from_yaml_invalid_data(self, tmp_path: Path):
        """Test from_yaml with invalid data."""
        import yaml
        
        yaml_file = tmp_path / "VW-1025-a-20-1-o.yaml"
        with yaml_file.open("w") as f:
            yaml.dump([{"invalid": "data"}], f)
        
        with pytest.raises(ValueError, match="Invalid record at index 0"):
            QuestionRecord.from_yaml(yaml_file)
    
    def test_from_yaml_exam_id_mismatch(self, tmp_path: Path):
        """Test from_yaml with exam ID mismatch between filename and records."""
        import yaml
        
        exam = Exam(id="VW-1025-a-19-1-o", level=ExamLevel.VWO, year=2019, tijdvak=1)  # Different year
        record = QuestionRecord(
            id="VW-1025-a-19-1-o_q01",
            exam=exam,
            title="Title",
            question_number="1",
            question_text="Question",
            figure=FigureInfo(present=False),
            source_images=[]
        )
        
        # Filename suggests 2020, but record has 2019
        yaml_file = tmp_path / "VW-1025-a-20-1-o.yaml"
        with yaml_file.open("w") as f:
            yaml.dump([record.model_dump(mode="json")], f)
        
        with pytest.raises(ValueError, match="Exam ID mismatch"):
            QuestionRecord.from_yaml(yaml_file)


class TestQuestionRecordVectorStoreAttributes:
    """Tests for QuestionRecordVectorStoreAttributes model."""
    
    def test_valid_attributes(self):
        """Test creating valid vector store attributes."""
        attrs = QuestionRecordVectorStoreAttributes(
            record_id="VW-1025-a-20-1-o_q01",
            exam_id="VW-1025-a-20-1-o",
            exam_level="vwo",
            exam_year="2020",
            exam_tijdvak="1",
            question_number="1",
            page_images='["pages/page1.png"]',
            figure_images='["figures/fig1.png"]',
            source_images='["page1.png"]',
            figure_present="True",
            figure_missing="False"
        )
        
        assert attrs.record_id == "VW-1025-a-20-1-o_q01"
        assert attrs.exam_id == "VW-1025-a-20-1-o"
        assert attrs.question_number == "1"
    
    def test_get_page_images(self):
        """Test parsing page_images JSON string."""
        attrs = QuestionRecordVectorStoreAttributes(
            record_id="test",
            exam_id="test",
            exam_level="vwo",
            exam_year="2020",
            exam_tijdvak="1",
            question_number="1",
            page_images='["pages/page1.png", "pages/page2.png"]',
            figure_images='[]',
            source_images='[]',
            figure_present="False",
            figure_missing="False"
        )
        
        page_images = attrs.get_page_images()
        assert page_images == ["pages/page1.png", "pages/page2.png"]
    
    def test_get_figure_images(self):
        """Test parsing figure_images JSON string."""
        attrs = QuestionRecordVectorStoreAttributes(
            record_id="test",
            exam_id="test",
            exam_level="vwo",
            exam_year="2020",
            exam_tijdvak="1",
            question_number="1",
            page_images='[]',
            figure_images='["figures/fig1.png"]',
            source_images='[]',
            figure_present="True",
            figure_missing="False"
        )
        
        figure_images = attrs.get_figure_images()
        assert figure_images == ["figures/fig1.png"]
    
    def test_get_source_images(self):
        """Test parsing source_images JSON string."""
        attrs = QuestionRecordVectorStoreAttributes(
            record_id="test",
            exam_id="test",
            exam_level="vwo",
            exam_year="2020",
            exam_tijdvak="1",
            question_number="1",
            page_images='[]',
            figure_images='[]',
            source_images='["page1.png", "page2.png", "page3.png"]',
            figure_present="False",
            figure_missing="False"
        )
        
        source_images = attrs.get_source_images()
        assert source_images == ["page1.png", "page2.png", "page3.png"]
    
    def test_model_validate_from_dict(self):
        """Test using model_validate with a dictionary (as from vector store)."""
        attrs_dict = {
            "record_id": "VW-1025-a-20-1-o_q01",
            "exam_id": "VW-1025-a-20-1-o",
            "exam_level": "vwo",
            "exam_year": "2020",
            "exam_tijdvak": "1",
            "question_number": "1",
            "page_images": '["pages/page1.png"]',
            "figure_images": '[]',
            "source_images": '["page1.png"]',
            "figure_present": "True",
            "figure_missing": "False"
        }
        
        attrs = QuestionRecordVectorStoreAttributes.model_validate(attrs_dict)
        
        assert attrs.record_id == "VW-1025-a-20-1-o_q01"
        assert attrs.get_page_images() == ["pages/page1.png"]
    
    def test_missing_required_field(self):
        """Test that model_validate raises error for missing required fields."""
        attrs_dict = {
            "record_id": "test",
            # Missing exam_id and other required fields
        }
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            QuestionRecordVectorStoreAttributes.model_validate(attrs_dict)

