from collections import Counter
from typing import Callable, TypeVar
import uuid

from agents import Agent, Runner, TResponseInputItem # type: ignore
from loguru import logger

from exercise_finder.agents.config import agent_name_to_event_mapping
from exercise_finder.pydantic_models import ConversationEvent
from exercise_finder.types import ConversationHistory


T = TypeVar("T", bound=ConversationEvent)


def init_conversation_history(
    exercise_finder_session_id: uuid.UUID, user_name: str
) -> ConversationHistory:
    """Initialize conversation history with a session start event."""
    return [
    ]


def add_event_to_conversation_history(
    conversation_history: ConversationHistory,
    event: T,
) -> ConversationHistory:
    """Immutable append of an event to the conversation history."""
    return [*conversation_history, event]


def build_conversation_history(
    conversation_history: ConversationHistory,
) -> list[TResponseInputItem]:
    """
    Build a conversation history from a text string.

    Note: TResponseInputItem is a type alias, we can't initialize it directly.

    Args:
        text: str

    Returns:
        list[TResponseInputItem]
    """
    text = "\n".join([event.render() for event in conversation_history])
    return [
        {
            "role": "user",
            "content": [{"type": "input_text", "text": text}],
        }
    ]


def filter_conversation_history(
    conversation_history: ConversationHistory,
    agent: Agent,
) -> ConversationHistory:
    """
    Filter the conversation history to only include events that the agent requires to function.

    Args:
        conversation_history: ConversationHistory
        agent: Agent

    Returns:
        ConversationHistory
    """
    allowed_event_types = agent_name_to_event_mapping[agent.name]  # type: ignore

    kept = [
        event for event in conversation_history if type(event) in allowed_event_types
    ]

    kept_type_counts = Counter(type(event).__name__ for event in kept)
    removed = [
        event
        for event in conversation_history
        if type(event) not in allowed_event_types
    ]
    removed_type_counts = Counter(type(event).__name__ for event in removed)

    logger.debug(
        "Filtered conversation history for agent={agent_name}: total_in={total_in} kept={kept} removed={removed} "
        "kept_types={kept_types} removed_types={removed_types}",
        agent_name=agent.name,
        total_in=len(conversation_history),
        kept=len(kept),
        removed=len(removed),
        kept_types=dict(kept_type_counts),
        removed_types=dict(removed_type_counts),
    )

    return kept


OutputT = TypeVar("OutputT")


async def run_agent_pipeline(
    *,
    agent: Agent,
    conversation_history: ConversationHistory,
    event_factory: Callable[[OutputT], ConversationEvent] | None = None,
    input_builder: Callable[
        [ConversationHistory], list[TResponseInputItem]
    ] = build_conversation_history,
) -> tuple[OutputT, ConversationHistory]:
    """
    Shared flow: filter history -> build input -> run agent -> append event.

    Args:
        agent: Agent instance to execute.
        conversation_history: immutable conversation log input.
        event_factory: optional factory to turn output into ConversationEvent. (dep injection)
        input_builder: builds the agent input payload from filtered history (dep injection).
    """
    # filter the conversation history to only include events that the agent requires to function
    filtered_history = filter_conversation_history(conversation_history, agent)

    # build the agent input
    input_items = input_builder(filtered_history)

    # run the agent
    run_result = await Runner.run(agent, input=input_items)
    output: OutputT = run_result.final_output  # type: ignore

    # add the event to the conversation history if an event factory is provided
    updated_history = (
        add_event_to_conversation_history(conversation_history, event_factory(output))
        if event_factory
        else conversation_history
    )

    return output, updated_history
