from __future__ import annotations

from pathlib import Path
import os
import json
import random
from typing import Any

from dotenv import load_dotenv # type: ignore[import-not-found]
from openai import OpenAI # type: ignore[import-not-found]

from exercise_finder.services.vectorstore.helpers import (
    _load_question_records,
    _write_index_files,
    _save_file_to_openai,
    _save_file_to_vector_store,
    _attributes_from_record,
)
from exercise_finder.services.format_questions.main import load_formatted_question_from_exam_and_question_number
from exercise_finder.pydantic_models import QuestionRecord
import exercise_finder.paths as paths

def _get_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in environment.")
    return OpenAI(api_key=api_key)


async def vectorstore_fetch(*,
    vector_store_id: str,
    query: str,
    max_results: int = 5,
    best: bool = True,
) -> dict:
    """
    Retrieve the best match, fetch full stored text, format into multipart structure,
    and print the result including resolved image paths.

    Steps:
    1. Search the vector store for a query
    2. Fetch the full stored text for the best hit
    3. Format the question text into a multipart question
    4. Return relative image paths (from metadata)
    """
    client = _get_client()

    # 1. Search the vector store for a query
    results = search_vector_store(
        client=client,
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=max_results,
    )
    if not results:
        raise ValueError("No results found.")

    # 2. Select the best (or random) result, then fetch the full stored text
    selected_result = results[0] if best else random.choice(results)
    attrs = selected_result.get("attributes") or {}
    exam_id = attrs.get("exam_id")
    question_number = attrs.get("question_number")
    
    # we require a question number to load the formatted question
    if not question_number:
        raise ValueError("Missing question_number in vector-store attributes.")

    # we require an exam id to load the formatted question
    if not exam_id:
        raise ValueError("Missing exam_id in vector-store attributes.")
    
    # 3. Load the formatted question
    formatted_question = load_formatted_question_from_exam_and_question_number(
        exam_id=exam_id,
        question_number=question_number,
    )

    # 4. Return relative image paths (from metadata)
    page_images = json.loads(attrs.get("page_images", "[]"))
    figure_images = json.loads(attrs.get("figure_images", "[]"))

    # return the result
    return {
        "record_id": attrs.get("record_id"),
        "exam_id": exam_id,
        "score": selected_result.get("score"),
        "formatted": formatted_question.model_dump(mode="json"),
        "page_images": page_images,
        "figure_images": figure_images,
    }


def create_vector_store(*, client: OpenAI, name: str, description: str = "exercise-finder") -> str:
    """
    Create an OpenAI vector store and return its id.

    Example:
    ```py
    vector_store_id = create_vector_store(client=client, name="vwo-2018-tv1")
    ```
    """
    vs = client.vector_stores.create(name=name, description=description)
    return vs.id  # type: ignore[return-value]


def add_jsonl_questions_to_vector_store(
    *,
    client: OpenAI,
    vector_store_id: str,
    jsonl_path: Path,
    index_files_dir: Path = paths.vectorstore_index_dir(),
) -> None:
    """
    Upload each QuestionRecord in JSONL as a separate text file and add it to the vector store.
    This preserves per-question metadata via vector-store file attributes.

    Inputs:
    - `jsonl_path`: a JSONL file where each line is a `QuestionRecord` (your output from `images-to-questions`)
    - `index_files_dir`: where we materialize the temporary `.txt` files that get uploaded

    Side effects:
    - Writes `data/vectorstore-index/<jsonl-stem>/<record_id>.txt`
    - Uploads each `.txt` to OpenAI Files
    - Attaches each file to the vector store with `attributes` including:
      - `record_id`, `question_number`, `exam_year`, ...
      - `page_images`, `figure_images` as JSON-encoded lists of relative paths

    Example:
    ```py
    add_jsonl_questions_to_vector_store(
        client=client,
        vector_store_id="vs_...",
        jsonl_path=Path("data/questions-extracted/VW-1025-a-18-1-o.jsonl"),
    )
    ```
    """
    records = _load_question_records(jsonl_path)
    add_question_records_to_vector_store(
        client=client,
        vector_store_id=vector_store_id,
        records=records,
        index_files_dir=index_files_dir,
        dataset_name=jsonl_path.stem,
    )


def add_question_records_to_vector_store(
    *,
    client: OpenAI,
    vector_store_id: str,
    records: list[QuestionRecord],
    index_files_dir: Path = paths.vectorstore_index_dir(),
    dataset_name: str = "questions",
) -> None:
    """
    Add already-parsed `QuestionRecord`s to an existing vector store.

    Use this when you have question records in memory (or loaded from `.json` instead of `.jsonl`)
    and want to attach them to an existing vector store.

    Example:
    ```py
    import json
    from pathlib import Path
    from exercise_finder.pydantic_models import QuestionRecord
    from exercise_finder.services.vectorstore.main import add_question_records_to_vector_store

    raw = json.loads(Path("questions.json").read_text(encoding="utf-8"))
    records = [QuestionRecord.model_validate(obj) for obj in raw]
    add_question_records_to_vector_store(
        client=client,
        vector_store_id="vs_...",
        records=records,
        dataset_name="vwo-2018-tv1",
    )
    ```
    """
    if not records:
        raise ValueError("No records provided.")

    out_dir = index_files_dir / dataset_name
    id_to_path = _write_index_files(records, out_dir)

    for record in records:
        file_path = id_to_path[record.id]
        file_id = _save_file_to_openai(client=client, file_path=file_path)
        _save_file_to_vector_store(
            client=client,
            vector_store_id=vector_store_id,
            file_id=file_id,
            attributes=_attributes_from_record(record),
        )


def search_vector_store(
    *,
    client: OpenAI,
    vector_store_id: str,
    query: str,
    max_num_results: int = 5,
) -> list[dict[str, Any]]:
    """
    Returns raw search results including file_id, score, attributes, and content chunks.

    Example:
    ```py
    results = search_vector_store(
        client=client,
        vector_store_id="vs_...",
        query="parametric equations",
        max_num_results=5,
    )
    best = results[0]
    print(best["file_id"], best["score"])
    print(best["attributes"]["record_id"])
    ```
    """
    page = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=max_num_results,
    )
    return [item.model_dump(mode="json") for item in page.data]  # type: ignore[attr-defined]


def fetch_index_file_text(*, client: OpenAI, vector_store_id: str, file_id: str) -> str:
    """
    Download the stored text for a vector-store file.

    This fetches the vector-store file content for `file_id` from `vector_store_id` and
    returns it as text. Use this when you want the *full* question text (not just a search snippet).

    Note:
    Files uploaded with `purpose="assistants"` are not downloadable via `client.files.content(...)`.
    Vector store files must be retrieved via `client.vector_stores.files.content(...)`.

    Example:
    ```py
    text = fetch_index_file_text(client=client, vector_store_id="vs_...", file_id=best["file_id"])
    print(text)
    ```
    """
    page = client.vector_stores.files.content(file_id, vector_store_id=vector_store_id)
    return "\n".join(item.text for item in page.data if item.type == "text").strip()
