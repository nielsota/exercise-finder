from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import json
from typing import Any
import yaml # type: ignore[import-untyped]

from pydantic import BaseModel, ConfigDict, model_validator # type: ignore

from exercise_finder.constants import pdf_acronym_to_level_mapping
from exercise_finder.enums import ExamLevel
from exercise_finder.utils.file_utils import get_files

class Exam(BaseModel):
    id: str
    year: int
    tijdvak: int
    level: ExamLevel

    @classmethod
    def from_file_path(cls, file_path: Path) -> "Exam":
        """Create an Exam from a file path."""
        parts = file_path.stem.split("-")
        return cls(
            id=file_path.stem,
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
    title: str
    figure: FigureInfo


class QuestionRecord(BaseModel):
    """
    A normalized, question-sized record suitable for indexing.
    """

    id: str
    exam: Exam
    title: str
    question_number: str
    question_text: str
    figure: FigureInfo
    source_images: list[str]
    page_images: list[str] | None = None
    figure_images: list[str] | None = None

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> list["QuestionRecord"]:
        """
        Load question records from a YAML file.
        
        YAML file should contain a list of QuestionRecord objects.
        
        Validates:
        - File exists and is a .yaml file
        - Filename matches exam naming convention
        - All records belong to the same exam
        
        Example:
            records = QuestionRecord.from_yaml(Path("data/questions-extracted/VW-1025-a-18-1-o.yaml"))
        """
        import yaml  # type: ignore[import-untyped]
        
        # Validate file exists
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        
        if not yaml_path.is_file():
            raise ValueError(f"Path is not a file: {yaml_path}")
        
        # Validate extension
        if yaml_path.suffix != ".yaml":
            raise ValueError(f"File must have .yaml extension, got: {yaml_path.suffix}")
        
        # Validate filename pattern matches exam naming
        exam = Exam.from_file_path(yaml_path)
        
        # Load and validate records
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise ValueError(f"YAML file is empty: {yaml_path}")
        
        if not isinstance(data, list):
            raise ValueError(f"YAML file must contain a list of records, got: {type(data)}")
        
        # Parse all records
        records = []
        for i, item in enumerate(data):
            try:
                records.append(cls.model_validate(item))
            except Exception as e:
                raise ValueError(f"Invalid record at index {i}: {e}")
        
        # Validate all records belong to same exam
        exam_ids = {record.exam.id for record in records}
        if len(exam_ids) > 1:
            raise ValueError(f"All records must belong to same exam. Found: {exam_ids}")
        
        expected_exam_id = exam.id
        if records[0].exam.id != expected_exam_id:
            raise ValueError(
                f"Exam ID mismatch. Filename suggests '{expected_exam_id}', "
                f"but records have '{records[0].exam.id}'"
            )
        
        return records

    @classmethod
    def from_exam_dir(cls, exam_dir: Path) -> list["QuestionRecord"]:
        """
        Load question records from an exam directory containing individual YAML files.
        
        Each YAML file contains a single QuestionRecord object (e.g., q1.yaml, q2.yaml).
        
        Validates:
        - Directory exists and contains .yaml files
        - Directory name matches exam naming convention
        - All records belong to the same exam
        
        Example:
            records = QuestionRecord.from_exam_dir(Path("data/questions-extracted/VW-1025-a-18-1-o/"))
        """
        import yaml  # type: ignore[import-untyped]
        
        # Validate directory exists
        if not exam_dir.exists():
            raise FileNotFoundError(f"Exam directory not found: {exam_dir}")
        
        if not exam_dir.is_dir():
            raise ValueError(f"Path is not a directory: {exam_dir}")
        
        # Validate directory name matches exam naming
        exam = Exam.from_file_path(exam_dir)
        
        # Load all YAML files in the directory
        yaml_files = sorted(exam_dir.glob("*.yaml"))
        if not yaml_files:
            raise ValueError(f"No YAML files found in {exam_dir}")
        
        # Parse all records
        records = []
        for yaml_file in yaml_files:
            with yaml_file.open("r") as f:
                data = yaml.safe_load(f)
                try:
                    record = cls.model_validate(data)
                    records.append(record)
                except Exception as e:
                    raise ValueError(f"Invalid record in {yaml_file.name}: {e}")
        
        # Validate all records belong to same exam
        exam_ids = {record.exam.id for record in records}
        if len(exam_ids) > 1:
            raise ValueError(f"All records must belong to same exam. Found: {exam_ids}")
        
        expected_exam_id = exam.id
        if records[0].exam.id != expected_exam_id:
            raise ValueError(
                f"Exam ID mismatch. Directory suggests '{expected_exam_id}', "
                f"but records have '{records[0].exam.id}'"
            )
        
        return records

    def to_text(self) -> str:
        """Convert a question record to a text string for vector store indexing."""
        parts = [self.title.strip(), self.question_text.strip()]
        if self.figure and self.figure.description:
            parts.append("\n\n[FIGURE]\n" + self.figure.description.strip())
        return "\n".join(parts).strip() + "\n"


    def attributes_for_vector_store(self) -> dict[str, Any]:
        """Convert a question record to a dictionary of attributes for the vector store."""
        return {
            "record_id": self.id,
            "exam_id": self.exam.id,
            "exam_level": self.exam.level.value,
            "exam_year": str(self.exam.year),
            "exam_tijdvak": str(self.exam.tijdvak),
            "question_number": str(self.question_number),
            "page_images": json.dumps(self.page_images or [], ensure_ascii=False),
            "figure_images": json.dumps(self.figure_images or [], ensure_ascii=False),
            "source_images": json.dumps(self.source_images or [], ensure_ascii=False),
            "figure_present": str(bool(self.figure.present)),
            "figure_missing": str(bool(self.figure.missing)),
    }


class QuestionRecordVectorStoreAttributes(BaseModel):
    """
    Validated attributes from a vector store result.
    
    These are the metadata fields stored alongside each question in the vector store.
    """
    record_id: str
    exam_id: str
    exam_level: str
    exam_year: str
    exam_tijdvak: str
    question_number: str
    page_images: str  # JSON string
    figure_images: str  # JSON string
    source_images: str  # JSON string
    figure_present: str
    figure_missing: str
    
    def get_page_images(self) -> list[str]:
        """Parse page_images JSON string to list."""
        return json.loads(self.page_images)
    
    def get_figure_images(self) -> list[str]:
        """Parse figure_images JSON string to list."""
        return json.loads(self.figure_images)
    
    def get_source_images(self) -> list[str]:
        """Parse source_images JSON string to list."""
        return json.loads(self.source_images)


class MultipartQuestionPart(BaseModel):
    """A single part of a multipart question."""
    text: str
    label: str | None = None  # Auto-generated (a, b, c) if None
    points: int = 0
    
    model_config = ConfigDict(extra="forbid")


class AgentMultipartQuestionOutput(BaseModel):
    """
    Agent output for multipart question formatting.
    
    This is what the LLM agent returns - ONLY the formatted text content.
    The agent's job is to parse question text into structured parts (title, stem, parts).
    
    Metadata like exam_id, calculator_allowed, and image paths are NOT generated
    by the agent - they are added afterward from QuestionRecord.
    
    Use MultipartQuestionOutput (which extends this) for the full model with metadata.
    """
    title: str
    stem: str
    parts: list[MultipartQuestionPart]
    
    model_config = ConfigDict(extra="forbid")
    
    @model_validator(mode="after")
    def auto_generate_part_labels(self) -> "AgentMultipartQuestionOutput":
        """Auto-generate labels (a, b, c) for parts without explicit labels."""
        for i, part in enumerate(self.parts):
            if part.label is None:
                part.label = chr(ord('a') + i)
        return self


class MultipartQuestionOutput(AgentMultipartQuestionOutput):
    """
    Complete multipart question model with metadata.
    
    This extends AgentMultipartQuestionOutput by adding metadata fields that are
    NOT generated by the LLM agent:
    - exam_id, calculator_allowed: Question metadata
    - page_images, figure_images: Forwarded from QuestionRecord
    
    Used for:
    - Storing formatted questions (YAML files)
    - Practice exercises
    - Vectorstore operations
    - Web display
    """
    # Optional metadata (not generated by agent)
    exam_id: str | None = None
    calculator_allowed: bool | None = None
    
    # Image paths (forwarded from QuestionRecord, not agent-generated)
    page_images: list[str] = []
    figure_images: list[str] = []
    
    model_config = ConfigDict(extra="forbid")
    
    @property
    def max_marks(self) -> int:
        """Computed property: sum of all part points."""
        return sum(part.points for part in self.parts)


class PracticeExerciseMetadata(BaseModel):
    """Metadata for a practice exercise set."""
    title: str
    subtitle: str
    
    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> "PracticeExerciseMetadata":
        """Load metadata from _meta.yaml file."""
        if not yaml_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {yaml_path}")
        
        with yaml_path.open("r") as f:
            data = yaml.safe_load(f)
        
        return cls.model_validate(data)


class PracticeExerciseSet(BaseModel):
    """Collection of practice exercises for a topic."""
    topic: str
    title: str
    subtitle: str
    exercises: list[MultipartQuestionOutput]
    
    def __add__(self, other: "PracticeExerciseSet") -> "PracticeExerciseSet":
        """
        Combine two PracticeExerciseSets.
        
        Validates that topic, title, and subtitle match before combining.
        Returns a new PracticeExerciseSet with combined exercises.
        """
        if not isinstance(other, PracticeExerciseSet):
            raise TypeError(f"Cannot add PracticeExerciseSet with {type(other)}")
        
        if self.topic != other.topic:
            raise ValueError(f"Cannot combine different topics: {self.topic} != {other.topic}")
        
        if self.title != other.title:
            raise ValueError(f"Cannot combine different titles: {self.title} != {other.title}")
        
        if self.subtitle != other.subtitle:
            raise ValueError(f"Cannot combine different subtitles: {self.subtitle} != {other.subtitle}")
        
        return PracticeExerciseSet(
            topic=self.topic,
            title=self.title,
            subtitle=self.subtitle,
            exercises=self.exercises + other.exercises,
        )
    
    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> "PracticeExerciseSet":
        """Load exercise set from YAML file with validation."""
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
    
    @classmethod
    def load_from_directory(cls, topic_dir: Path) -> "PracticeExerciseSet":
        """
        Load practice exercises from a directory of individual YAML files.
        
        Directory structure:
            data/practice-exercises/unitcircle/
              ├── p1.yaml
              ├── p2.yaml
              └── ...
        
        Each file contains a single MultipartQuestionOutput.
        The directory name is used as the topic slug.
        
        Returns a PracticeExerciseSet with exercises loaded in sorted order.
        
        Example:
            exercise_set = PracticeExerciseSet.load_from_directory(
                Path("data/practice-exercises/unitcircle/")
            )
        """
        # Validate directory exists
        if not topic_dir.exists():
            raise FileNotFoundError(f"Topic directory not found: {topic_dir}")
        
        if not topic_dir.is_dir():
            raise ValueError(f"Path is not a directory: {topic_dir}")
        
        # Use directory name as topic
        topic = topic_dir.name
            
        # Load metadata
        metadata = PracticeExerciseMetadata.load_from_yaml(topic_dir / "_meta.yaml")

        # Load all practice YAML files (p*.yaml) and combine them
        yaml_files = sorted(topic_dir.glob("p*.yaml"))
        if not yaml_files:
            raise ValueError(f"No practice exercise files found in {topic_dir}")
        
        # Load each file and add to the result
        exercises = []
        for yaml_file in yaml_files:
            try:
                # Load each file as a single-exercise set (each file contains one MultipartQuestionOutput)
                with yaml_file.open("r") as f:
                    data = yaml.safe_load(f)
                    exercises.append(MultipartQuestionOutput.model_validate(data))
                
            except Exception as e:
                raise ValueError(f"Invalid exercise in {yaml_file.name}: {e}")
        
        return cls(
            topic=topic,
            title=metadata.title,
            subtitle=metadata.subtitle,
            exercises=exercises,
        )


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
            # Get all files, filtering out system files (with_ignore=True by default)
            all_files = get_files(pages_dir, pattern="*", with_ignore=True)
            non_png_pages = [f for f in all_files if f.suffix.lower() != ".png"]
            if non_png_pages:
                raise ValueError(
                    f"Non-PNG files found in pages directory: {[f.name for f in non_png_pages]}"
                )
        
        # validate only png images exist in the figures directory
        if self.figures:
            figures_dir = self.figures[0].parent
            # Get all files, filtering out system files (with_ignore=True by default)
            all_files = get_files(figures_dir, pattern="*", with_ignore=True)
            non_png_figures = [f for f in all_files if f.suffix.lower() != ".png"]
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

