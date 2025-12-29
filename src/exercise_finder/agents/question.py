# mypy: ignore-errors
import dotenv
from agents import Agent, ModelSettings, FileSearchTool

from exercise_finder.enums import OpenAIModel, AgentName 
from exercise_finder.pydantic_models import (
    QuestionOutput,
    QuestionEvent,
)
from exercise_finder.types import PromptGetter, AgentGetter, ConversationHistory
from exercise_finder.agents.utils import (
    run_agent_pipeline,
)
from exercise_finder.agents.config import agent_name_to_model_mapping

dotenv.load_dotenv()


def get_system_prompt() -> str:
    return f"""
        You are responsible for finding a question from a vector database of exams.

        The user will provide you with a message and you will need to find a question from the vector database that matches the message.

        The output should be a JSON object that matches the QuestionOutput schema.
        {QuestionOutput.model_json_schema()}
        """


class QuestionAgent(Agent):
    def __init__(self, model: OpenAIModel, prompt_getter: PromptGetter, vector_store_id: str):
        super().__init__(
            name=AgentName.GET_QUESTION_AGENT,
            instructions=prompt_getter(),
            model=model.value,
            model_settings=ModelSettings(store=True),
            output_type=QuestionOutput,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=[vector_store_id],
                    include_search_results=True,
                )
            ],
        )


async def generate_question(
    conversation_history: ConversationHistory,
    vector_store_id: str,
    model: OpenAIModel = agent_name_to_model_mapping[AgentName.GET_QUESTION_AGENT],
    prompt_getter: PromptGetter = get_system_prompt,
    agent_getter: AgentGetter = QuestionAgent,
) -> tuple[QuestionOutput, ConversationHistory]:
    """
    Generate a question from a message using a prompt getter and agent getter.

    Args:
        conversation_history: ConversationHistory
        model: OpenAIModel
        prompt_getter: PromptGetter
        agent_getter: AgentGetter
    """
    # build the agent
    trivia_agent = agent_getter(model=model, prompt_getter=prompt_getter, vector_store_id=vector_store_id)

    return await run_agent_pipeline(
        agent=trivia_agent,
        conversation_history=conversation_history,
        event_factory=QuestionEvent.from_output,  # type: ignore[arg-type]
    )

if __name__ == "__main__":
    import os
    import asyncio
    from dotenv import load_dotenv # type: ignore[import-not-found]
    from openai import OpenAI # type: ignore[import-not-found]

    from exercise_finder.pydantic_models import UserMessageEvent

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    vector_store_id = "vs_694a810fe33881918749111bbf5a849c"
    conversation_history = [UserMessageEvent(message="I want to find a question involving parametric equations")]
    question, conversation_history = asyncio.run(generate_question(conversation_history, vector_store_id, model=OpenAIModel.GPT_5_MINI, prompt_getter=get_system_prompt, agent_getter=QuestionAgent))
    print(question.model_dump_json(indent=2))