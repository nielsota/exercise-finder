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



########################################################
# Conversation Events - used for context engineering
########################################################


class ConversationEvent(BaseModel):
    # id is not required for new events, but is required for existing events
    # in order to recall what events already exist as part of the conversation session
    # in the database
    id: uuid.UUID | None = None

    def render(self) -> str:
        """
        Render the conversation event as a string.
        """
        raise NotImplementedError("Subclasses must implement render()")

    def from_output(self, output: Any) -> "ConversationEvent":
        """
        Create a conversation event from an output.
        """
        raise NotImplementedError("Subclasses must implement from_output()")


class UserMessageEvent(ConversationEvent):
    """A user message event is a conversation event that represents a message from the user."""

    message: str

    def render(self) -> str:
        return (
            "<user_message_event>\n"
            f"  message: {self.message}\n"
            "</user_message_event>"
        )

    @classmethod
    def from_output(self, output: UserInput) -> "UserMessageEvent":
        return UserMessageEvent(message=output.message)


class QuestionEvent(ConversationEvent):
    """A router event is a conversation event that represents a message from the router agent."""

    question: str
    exam: Exam

    def render(self) -> str:
        return (
            "<question_event>\n"
            f"  question: {self.question}\n"
            f"  exam: {self.exam}\n"
            "</question_event>"
        )

    @classmethod
    def from_output(self, output: QuestionOutput) -> "QuestionEvent":
        """
        Create a conversation event from a question output.
        """
        return QuestionEvent(
            question=output.question,
            exam=output.exam,
        )




if __name__ == "__main__":
    file_path = Path("vw-1025-a-25-2-o.pdf")
    exam = Exam.from_file_path(file_path)
    print(exam)
