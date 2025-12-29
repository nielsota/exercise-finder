# mypy: ignore-errors
from __future__ import annotations

import dotenv
from agents import Agent, ModelSettings, Runner, TResponseInputItem

from exercise_finder.enums import AgentName, OpenAIModel
from exercise_finder.pydantic_models import MultipartQuestionOutput

dotenv.load_dotenv()


def get_system_prompt() -> str:
    return f"""
You format Dutch math exam exercises into a multipart structure.

Input: raw question text that may contain a shared stem plus multiple subparts (a/b/c or 1/2/3).

Output a JSON object matching this schema exactly:
{MultipartQuestionOutput.model_json_schema()}

Rules:
- `stem` contains only the shared setup/context before the first subpart.
- `parts` contains each subpart in order; preserve wording and any points annotations (e.g. '4p').
- If there are no explicit subparts, put the entire text into `stem` and set `parts` to an empty list.
- Preserve ALL LaTeX delimiters exactly as given: \\( ... \\), \\[ ... \\], $ ... $, $$ ... $$.
- Do not solve the problem.
- The question text is in Dutch - keep it in Dutch.
""".strip()


class FormatMultipartAgent(Agent):
    def __init__(self, model: OpenAIModel, prompt: str = get_system_prompt()):
        super().__init__(
            name=AgentName.FORMAT_MULTIPART_QUESTION_AGENT,
            instructions=prompt,
            model=model.value,
            model_settings=ModelSettings(store=True),
            output_type=MultipartQuestionOutput,
            tools=[],
        )


async def format_multipart_question(
    *,
    question_text: str,
    model: OpenAIModel = OpenAIModel.GPT_5_MINI,
    prompt: str = get_system_prompt(),
) -> MultipartQuestionOutput:
    """
    Convert a raw (possibly multipart) question text into a structured stem + parts list.

    This is intended as step 2 of a 2-step pipeline:
    1) vision OCR -> `question_text`
    2) this function -> `{stem, parts[]}` for nicer UI rendering

    Example:
    ```py
    import asyncio
    from exercise_finder.agents.format_multipart import format_multipart_question

    formatted = asyncio.run(
        format_multipart_question(
            question_text=\"\"\"Buigraaklijn ... 4p 1 Bewijs dit. 5p 2 Stel ...\"\"\"
        )
    )
    print(formatted.stem)
    for part in formatted.parts:
        print(part.label, part.text)
    ```
    """
    agent = FormatMultipartAgent(model=model, prompt=prompt)
    input_items: list[TResponseInputItem] = [
        {"role": "user", "content": [{"type": "input_text", "text": question_text}]}
    ]
    run_result = await Runner.run(agent, input=input_items)
    return run_result.final_output  # type: ignore[return-value]
