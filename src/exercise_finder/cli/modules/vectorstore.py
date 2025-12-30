"""Vector store commands."""
from __future__ import annotations

import asyncio
import json

from pathlib import Path

import typer  # type: ignore[import-not-found]

from exercise_finder.services.vectorstore.main import (
    create_vector_store,
    add_jsonl_questions_to_vector_store,
    vectorstore_fetch,
    search_vector_store,
)
from exercise_finder.services.format_questions.main import load_formatted_question_from_exam_and_question_number
from exercise_finder.config import update_vector_store_id
import exercise_finder.paths as paths
from .utils import get_openai_client


app = typer.Typer(help="Vector store operations")


@app.command("create")
def create(
    name: str = typer.Option(..., "--name", help="Vector store name."),
    update_id: bool = typer.Option(
        False, 
        "--update-id", 
        help="Update the vector store ID in AWS Parameter Store (requires USE_SSM=true)"
    ),
) -> None:
    """
    Create a new vector store and optionally update the ID in AWS Parameter Store.
    
    Returns the vector store ID for use in subsequent commands.
    """
    client = get_openai_client()
    vector_store_id = create_vector_store(client=client, name=name)
    typer.echo(f"Created vector store: {vector_store_id}")
    
    if update_id:
        try:
            update_vector_store_id(vector_store_id)
            typer.echo("✓ Updated AWS Parameter Store with new ID")
        except ValueError as e:
            typer.echo(f"⚠ Could not update Parameter Store: {e}", err=True)
            typer.echo(f"You can manually set VECTOR_STORE_ID={vector_store_id}", err=True)
        


@app.command("add")
def add(
    vector_store_id: str = typer.Option(..., "--vector-store-id", "--id"),
    jsonl_dir: Path = typer.Option(
        paths.questions_extracted_dir(),
        "--jsonl-dir",
        exists=True,
        readable=True,
        help="Directory containing JSONL files (one QuestionRecord per line).",
    ),
) -> None:
    """Add questions from a directory of JSONL files to an existing vector store."""
    client = get_openai_client()
    for jsonl_path in jsonl_dir.glob("*.jsonl"):
        add_jsonl_questions_to_vector_store(
            client=client,
            vector_store_id=vector_store_id,
            jsonl_path=jsonl_path,
        )


@app.command("search")
def search(
    vector_store_id: str = typer.Option(..., "--vector-store-id"),
    query: str = typer.Option(..., "--query"),
    max_results: int = typer.Option(5, "--max-results"),
) -> None:
    """Search the vector store for a query."""
    client = get_openai_client()
    results = search_vector_store(
        client=client,
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=max_results,
    )
    typer.echo(json.dumps(results, ensure_ascii=False, indent=2))


@app.command("fetch")
def fetch(
    vector_store_id: str = typer.Option(..., "--vector-store-id"),
    query: str = typer.Option(..., "--query"),
    exams_root: Path = typer.Option(
        paths.questions_images_root(),
        "--exams-root",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Folder that contains multiple exam folders, e.g. data/questions-images",
    ),
    max_results: int = typer.Option(5, "--max-results"),
    best: bool = typer.Option(True, "--best", help="Fetch the best match or a random match."),
) -> None:
    """
    Retrieve the best match, fetch full stored text, format into multipart structure,
    and print the result including resolved image paths.

    Steps:
    1. Search the vector store for a query (vectorstore service)
    2. Load the formatted question (format_questions service)
    3. Resolve image paths for display/attachment
    4. Print the result
    """
    # Step 1: Search vector store (vectorstore service)
    search_result = asyncio.run(
        vectorstore_fetch(
            vector_store_id=vector_store_id,
            query=query,
            max_results=max_results,
            best=best,
        )
    )
    
    # Step 2: Load formatted question (format_questions service)
    formatted_question = load_formatted_question_from_exam_and_question_number(
        exam_id=search_result["exam_id"],
        question_number=search_result["question_number"],
    )
    
    # Step 3: Compose results
    exam_id = search_result["exam_id"]
    result = {
        **search_result,
        "formatted": formatted_question.model_dump(mode="json"),
        "page_images": [
            str(paths.exam_asset_under_root(exams_root, exam_id, p).resolve())
            for p in search_result["page_images"]
        ],
        "figure_images": [
            str(paths.exam_asset_under_root(exams_root, exam_id, p).resolve())
            for p in search_result["figure_images"]
        ],
    }
    
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))

