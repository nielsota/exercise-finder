# mypy: ignore-errors
from __future__ import annotations

from typing import Awaitable, Callable, Concatenate

from agents import Agent

from exercise_finder.pydantic_models import ConversationEvent

type PromptGetter = Callable[..., str]
type AgentGetter = Callable[..., Agent]

type ConversationHistory = list[ConversationEvent]

# A generation function that returns just a result
type AsyncGenerationFunction[**P, R] = Callable[
    Concatenate[ConversationHistory, P],
    Awaitable[R],
]

# A generation function that returns (result, updated_history)
type AsyncHistoryGenerationFunction[**P, R] = Callable[
    Concatenate[ConversationHistory, P],
    Awaitable[tuple[R, ConversationHistory]],
]
