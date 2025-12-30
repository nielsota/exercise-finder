# mypy: ignore-errors
from __future__ import annotations

import base64
from pathlib import Path

import dotenv
from agents import Agent, ModelSettings, Runner, TResponseInputItem

from exercise_finder.enums import OpenAIModel, AgentName
from exercise_finder.pydantic_models import QuestionFromImagesOutput

dotenv.load_dotenv()


def _guess_mime_type(path: Path) -> str:
    """
    Guess the MIME type of an image file based on its extension.
    
    Args:
        path: Path to the image file
        
    Returns:
        MIME type string (e.g., "image/png")
        
    Example:
        >>> _guess_mime_type(Path("photo.jpg"))
        'image/jpeg'
        >>> _guess_mime_type(Path("diagram.png"))
        'image/png'
        >>> _guess_mime_type(Path("unknown.xyz"))
        'application/octet-stream'
    """
    suffix = path.suffix.lower()
    if suffix in {".png"}:
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix in {".webp"}:
        return "image/webp"
    return "application/octet-stream"


def _image_path_to_data_url(path: Path) -> str:
    """
    Convert an image file to a base64-encoded data for API submission.
    
    Args:
        path: Path to the image file
        
    Returns:
        Data string (e.g., "data:image/png;base64,iVBORw0KG...")
    """
    mime = _guess_mime_type(path)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def get_system_prompt() -> str:
    return f"""
You transcribe Dutch math exam questions from one or more images.

Return a JSON object that matches this schema exactly:
{QuestionFromImagesOutput.model_json_schema()}

Rules:
- Preserve wording as faithfully as possible (verbatim transcription).
- The question title is often the first line of the question text (may be in bold or standalone). Extract it and place it ONLY in the `title` field, NOT in the `question_text` field.
- The `question_text` field should start with the content AFTER the title.
- Keep line breaks/bullets where they carry meaning (subparts a/b/c, given/asked).
- The provided images may contain a full multipart exercise; include ALL parts you can see in `question_text` (e.g. a/b/c or 1/2/3) in the original order.
- Do not stop after the first part; continue until the last visible part in the images.
- For math: wrap ALL math expressions in LaTeX delimiters so they render correctly:
  - Inline math: \\( x^2 \\), \\( \\frac{{a}}{{b}} \\)
  - Display/block math (standalone formulas): \\[ F = m \\cdot a \\]
  Do not use bare LaTeX without delimiters. Do not invent symbols.
- If there is a figure/diagram: set figure.present=true and describe it briefly in figure.description.
- If a figure is referenced but not visible/unclear: set figure.present=true and figure.missing=true; describe what you can.
- Do not solve the problem; only transcribe/describe.
""".strip()


class ImagesToQuestionAgent(Agent):
    def __init__(self, model: OpenAIModel, prompt: str = get_system_prompt()):
        super().__init__(
            name=AgentName.IMAGES_TO_QUESTION_AGENT,
            instructions=prompt,
            model=model.value,
            model_settings=ModelSettings(store=True),
            output_type=QuestionFromImagesOutput,
            tools=[],
        )


async def transcribe_question_images(
    *,
    page_images: list[Path],
    figure_images: list[Path] | None = None,
    model: OpenAIModel = OpenAIModel.GPT_4O,
    prompt: str = get_system_prompt(),
) -> QuestionFromImagesOutput:
    """
    Vision transcription for a single question folder (one multipart exercise).

    Inputs:
    - `page_images`: required; images that contain the question text (may span multiple pages)
    - `figure_images`: optional; images that contain only the diagram/figure(s)

    Output:
    - `QuestionFromImagesOutput.question_text`: verbatim transcription including *all* visible parts
    - `QuestionFromImagesOutput.figure`: whether a figure is present/missing + a short description

    Example:
    ```py
    import asyncio
    from pathlib import Path
    from exercise_finder.agents.images_to_question import transcribe_question_images

    result = asyncio.run(
        transcribe_question_images(
            page_images=[Path(".../q03/pages/page4.png")],
            figure_images=[Path(".../q03/figures/fig1.png")],
        )
    )
    print(result.question_text)
    print(result.figure)
    ```
    """
    if not page_images:
        raise ValueError("page_images must not be empty.")

    agent = ImagesToQuestionAgent(model=model, prompt=prompt)

    figure_images = figure_images or []

    content: list[dict] = [
        {
            "type": "input_text",
            "text": (
                "Transcribe this exam question from the images.\n"
                f"- Page images: {len(page_images)} (these contain the question text)\n"
                f"- Figure images: {len(figure_images)} (diagrams referenced by the question)\n"
            ),
        }
    ]
    for path in [*page_images, *figure_images]:
        content.append({"type": "input_image", "image_url": _image_path_to_data_url(path)})

    input_items: list[TResponseInputItem] = [{"role": "user", "content": content}]

    run_result = await Runner.run(agent, input=input_items)
    return run_result.final_output  # type: ignore[return-value]
