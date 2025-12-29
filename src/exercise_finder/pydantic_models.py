from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from pydantic import BaseModel, model_validator # type: ignore

from exercise_finder.constants import pdf_acronym_to_level_mapping
from exercise_finder.enums import ExamLevel

class Exam(BaseModel):
    year: int
    tijdvak: int
    level: ExamLevel

    @classmethod
    def from_file_path(cls, file_path: Path) -> "Exam":
        """Create an Exam from a file path."""
        parts = file_path.stem.split("-")
        return cls(
            level=pdf_acronym_to_level_mapping[parts[0].lower()],
            year=datetime.strptime(parts[3], "%y").year,
            tijdvak=int(parts[4]),
        )

    def __str__(self) -> str:
        return f"exam_{self.level.value}_{self.year}_tijdvak_{self.tijdvak}.pdf"


########################################################
# Input/Output models (contracts) for the agents
########################################################


class UserInput(BaseModel):
    message: str


class RouterInput(BaseModel):
    message: str


class QuestionOutput(BaseModel):
    question: str
    exam: Exam


########################################################
# OCR / image-ingestion models
########################################################


class FigureInfo(BaseModel):
    present: bool
    missing: bool = False
    description: str | None = None


class QuestionFromImagesOutput(BaseModel):
    """
    Output contract for the image → question transcription agent.
    """

    question_text: str
    figure: FigureInfo
    confidence: float | None = None
    notes: str | None = None


class QuestionRecord(BaseModel):
    """
    A normalized, question-sized record suitable for indexing.
    """

    id: str
    exam: Exam
    question_number: str
    question_text: str
    figure: FigureInfo
    source_images: list[str]
    page_images: list[str] | None = None
    figure_images: list[str] | None = None


class MultipartQuestionPart(BaseModel):
    label: str
    text: str


class MultipartQuestionOutput(BaseModel):
    stem: str
    parts: list[MultipartQuestionPart]


########################################################
# Exam folder structure models
########################################################

class QuestionFolderStructure(BaseModel):
    """
    A question folder structure.

    Example:
    |-- q01/
    |   |-- pages/
    |   |   |-- page1.png
    |   |   |-- page2.png
    |   |-- figures/
    |   |   |-- figure1.png
    |   |   |-- figure2.png
    """
    number: str
    root: Path
    pages: list[Path]
    figures: list[Path]

    @classmethod
    def from_question_dir(cls, question_dir: Path) -> "QuestionFolderStructure":
        """Create a QuestionFolderStructure from a question directory."""
        return cls(
            number=question_dir.name,
            root=question_dir,
            pages=list(question_dir.glob("pages/*.png")),
            figures=list(question_dir.glob("figures/*.png")),
        )
    
    def get_question_number(self) -> str:
        """
        Extract the numeric question number from the directory name.
        
        Example:
            >>> q = QuestionFolderStructure.from_question_dir(Path("q01"))
            >>> q.get_question_number()
            '1'
        """
        match = re.fullmatch(r"q(\d+)", self.number.lower())
        if not match:
            raise ValueError(f"Question directory must match qNN, got: {self.number}")
        return str(int(match.group(1)))
    
    def paths_relative_to(self, base: Path) -> dict[str, list[str]]:
        """
        Get paths relative to a base directory for serialization.
        
        Args:
            base: Base directory (typically exam root)
            
        Returns:
            Dictionary with 'pages', 'figures', and 'all' as relative path strings
            
        Example:
            >>> base = Path("/data/exams/VW-1025-a-18-1-o")
            >>> q = QuestionFolderStructure.from_question_dir(base / "q01")
            >>> q.paths_relative_to(base)
            {
                'pages': ['q01/pages/page1.png'],
                'figures': ['q01/figures/fig1.png'],
                'all': ['q01/pages/page1.png', 'q01/figures/fig1.png']
            }
        """
        return {
            'pages': [str(p.relative_to(base)) for p in self.pages],
            'figures': [str(p.relative_to(base)) for p in self.figures],
            'all': [str(p.relative_to(base)) for p in [*self.pages, *self.figures]],
        }


    @model_validator(mode="after")
    def validate_pages_directory(self) -> "QuestionFolderStructure":
        """Validate that the pages directory exists."""
        if not self.pages:
            raise ValueError(f"No pages directory found in {self.number}")
        return self

    @model_validator(mode="after")
    def validate_only_png_images(self) -> "QuestionFolderStructure":
        """Validate that only PNG images exist in the pages and figures directories."""
        
        # validate only png images exist in the pages directory; never null
        # but still include the check so other validators can check that the directory exists
        if self.pages:
            pages_dir = self.pages[0].parent
            non_png_pages = [f for f in pages_dir.iterdir() if f.is_file() and f.suffix.lower() != ".png"]
            if non_png_pages:
                raise ValueError(
                    f"Non-PNG files found in pages directory: {[f.name for f in non_png_pages]}"
                )
        
        # validate only png images exist in the figures directory
        if self.figures:
            figures_dir = self.figures[0].parent
            non_png_figures = [f for f in figures_dir.iterdir() if f.is_file() and f.suffix.lower() != ".png"]
            if non_png_figures:
                raise ValueError(
                    f"Non-PNG files found in figures directory: {[f.name for f in non_png_figures]}"
                )
        
        return self


class ExamFolderStructure(BaseModel):
    """
    A self-contained, validated exam folder structure.
    
    Contains all necessary information including:
    - Exam metadata (extracted from folder name)
    - Root directory path
    - All question subdirectories with validated structure
    
    Example:
        >>> exam = ExamFolderStructure.from_exam_dir(Path("data/VW-1025-a-18-1-o"))
        >>> exam.exam
        Exam(level=ExamLevel.VWO, year=2018, tijdvak=1)
        >>> len(exam.questions)
        3
    """
    name: str
    root: Path
    questions: list[QuestionFolderStructure]

    @classmethod
    def from_exam_dir(cls, exam_dir: Path) -> "ExamFolderStructure":
        """Create an ExamFolderStructure from an exam directory."""
        questions = sorted(
            [p for p in exam_dir.iterdir() if p.is_dir() and re.fullmatch(r"q\d+", p.name.lower())],
            key=lambda p: p.name,
        )
        return cls(
            name=exam_dir.name,
            root=exam_dir,
            questions=[QuestionFolderStructure.from_question_dir(q) for q in questions],
        )
    
    @property
    def exam(self) -> Exam:
        """
        Extract Exam metadata from the folder name.
        
        Uses the same parsing logic as Exam.from_file_path() by treating
        the directory name as a filename stem.
        
        Example:
            >>> exam_struct = ExamFolderStructure.from_exam_dir(Path("VW-1025-a-18-1-o"))
            >>> exam_struct.exam
            Exam(level=ExamLevel.VWO, year=2018, tijdvak=1)
        """
        return Exam.from_file_path(Path(f"{self.name}.pdf"))
    
    @property
    def exam_dir(self) -> Path:
        """
        Alias for root directory. Provides semantic clarity when used in context.
        
        Example:
            >>> exam_struct = ExamFolderStructure.from_exam_dir(Path("data/exams/VW-1025-a-18-1-o"))
            >>> exam_struct.exam_dir
            Path('data/exams/VW-1025-a-18-1-o')
        """
        return self.root

    @model_validator(mode="after")
    def validate_no_extra_directories(self) -> "ExamFolderStructure":
        """Validate that no directories other than questions exist in the exam directory."""
        all_dirs = [d for d in self.root.iterdir() if d.is_dir()]
        question_dirs = {q.number for q in self.questions}
        extra_dirs = [d.name for d in all_dirs if d.name not in question_dirs]
        
        if extra_dirs:
            raise ValueError(
                f"Unexpected directories found in exam folder '{self.name}': {extra_dirs}. "
                f"Only question directories (q01, q02, etc.) are allowed."
            )
        
        return self

    @model_validator(mode="after")
    def validate_no_duplicate_questions(self) -> "ExamFolderStructure":
        """Validate that there are no duplicate question numbers."""
        question_numbers = [q.number for q in self.questions]
        duplicates = [num for num in question_numbers if question_numbers.count(num) > 1]
        
        if duplicates:
            unique_duplicates = list(set(duplicates))
            raise ValueError(
                f"Duplicate question numbers found in exam '{self.name}': {unique_duplicates}"
            )
        
        return self

