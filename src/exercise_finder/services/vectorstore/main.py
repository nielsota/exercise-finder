from __future__ import annotations

from pathlib import Path
import os
import random
from typing import Any

from dotenv import load_dotenv # type: ignore[import-not-found]
from openai import OpenAI # type: ignore[import-not-found]

from exercise_finder.pydantic_models import QuestionRecord, QuestionRecordVectorStoreAttributes
import exercise_finder.paths as paths

from .helpers import (
    write_index_files,
    save_file_to_openai,
    save_file_to_vector_store,
)

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
    Search the vector store and return the best matching question's metadata.

    This function ONLY handles vector store operations - it does NOT load
    formatted questions. Callers should compose this with format_questions
    service if they need formatted output.

    Steps:
    1. Search the vector store for a query
    2. Select best (or random) result
    3. Parse and validate attributes
    4. Return metadata with image paths

    Returns:
        Dictionary containing:
        - record_id: Question record ID
        - exam_id: Exam identifier
        - question_number: Question number
        - score: Search relevance score
        - page_images: List of page image paths
        - figure_images: List of figure image paths
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
    
    # 2. Select the best (or random) result, then parse and validate attributes
    selected_result = results[0] if best else random.choice(results)
    attrs_dict = selected_result.get("attributes") or {}
    
    # Validate attributes using Pydantic (will raise ValidationError if any required field is missing)
    attrs = QuestionRecordVectorStoreAttributes.model_validate(attrs_dict)

    # 3. Return vector store metadata (no formatting - that's another service's job)
    return {
        "record_id": attrs.record_id,
        "exam_id": attrs.exam_id,
        "question_number": attrs.question_number,
        "score": selected_result.get("score"),
        "page_images": attrs.get_page_images(),
        "figure_images": attrs.get_figure_images(),
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


def add_yaml_questions_to_vector_store(
    *,
    client: OpenAI,
    vector_store_id: str,
    exam_dir: Path,
    index_files_dir: Path = paths.vectorstore_index_dir(),
) -> None:
    """
    Upload each QuestionRecord from YAML files in an exam directory to the vector store.
    This preserves per-question metadata via vector-store file attributes.

    Inputs:
    - `exam_dir`: directory containing YAML files (e.g., data/questions-extracted/VW-1025-a-18-1-o/)
    - `index_files_dir`: where we materialize the temporary `.txt` files that get uploaded

    Side effects:
    - Writes `data/vectorstore-index/<exam-id>/<record_id>.txt`
    - Uploads each `.txt` to OpenAI Files
    - Attaches each file to the vector store with `attributes` including:
      - `record_id`, `question_number`, `exam_year`, ...
      - `page_images`, `figure_images` as JSON-encoded lists of relative paths

    Example:
    ```py
    add_yaml_questions_to_vector_store(
        client=client,
        vector_store_id="vs_...",
        exam_dir=Path("data/questions-extracted/VW-1025-a-18-1-o/"),
    )
    ```
    """
    # Load all records from the exam directory
    records = QuestionRecord.from_exam_dir(exam_dir)
    
    add_question_records_to_vector_store(
        client=client,
        vector_store_id=vector_store_id,
        records=records,
        index_files_dir=index_files_dir,
        dataset_name=exam_dir.name,
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
    """
    # create the index files directory
    out_dir = index_files_dir / dataset_name

    # write the index files
    id_to_path = write_index_files(records, out_dir)

    # upload the index files to OpenAI and add them to the vector store
    for record in records:
        file_path = id_to_path[record.id]
        file_id = save_file_to_openai(client=client, file_path=file_path)
        save_file_to_vector_store(
            client=client,
            vector_store_id=vector_store_id,
            file_id=file_id,
            attributes=record.attributes_for_vector_store(),
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
