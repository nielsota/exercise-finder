from __future__ import annotations

from datetime import datetime
from pathlib import Path
import uuid
from typing import Any

from pydantic import BaseModel # type: ignore

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
