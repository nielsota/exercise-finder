# mypy: ignore-errors
"""API v1 endpoints - JSON responses for programmatic access."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]
from starlette.responses import FileResponse  # type: ignore[import-not-found]

from exercise_finder.services.vectorstore.main import vectorstore_fetch
from exercise_finder.services.questionformatter.main import load_formatted_question_from_exam_and_question_number
from exercise_finder.config import get_vector_store_id, refresh_vector_store_id
import exercise_finder.paths as paths
from ..auth import require_authentication


class FetchRequest(BaseModel):
    """Request model for fetching questions from the vector store."""
    query: str
    mode: Literal["best", "random"] = "best"
    max_results: int = 5


def create_v1_router(exams_root: Path) -> APIRouter:
    """
    Create the API v1 router.
    
    Args:
        exams_root: Root directory for exam files
        
    Returns:
        APIRouter with v1 API endpoints
    """
    router = APIRouter(prefix="/api/v1", tags=["api-v1"])

    @router.post("/fetch")
    async def fetch(
        payload: FetchRequest,
        authenticated: bool = Depends(require_authentication),
    ) -> dict:
        """
        Fetch a question from the vector store.

        This endpoint searches the vector store and returns formatted question data.
        """
        query = payload.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Missing query")
        if payload.max_results < 1 or payload.max_results > 20:
            raise HTTPException(status_code=400, detail="max_results must be between 1 and 20")

        vs_id: str = get_vector_store_id()
        
        # Step 1: Search vector store (vectorstore service)
        search_result = await vectorstore_fetch(
            vector_store_id=vs_id,
            query=query,
            max_results=payload.max_results,
            best=(payload.mode == "best"),
        )
        
        # Step 2: Load formatted question (format_questions service)
        formatted_question = load_formatted_question_from_exam_and_question_number(
            exam_id=search_result["exam_id"],
            question_number=search_result["question_number"],
        )
        
        # Step 3: Compose and return
        exam_id = search_result["exam_id"]
        return {
            **search_result,
            "formatted": formatted_question.model_dump(mode="json"),
            "page_images": [f"/image/{exam_id}/{p}" for p in search_result["page_images"]],
            "figure_images": [f"/image/{exam_id}/{p}" for p in search_result["figure_images"]],
        }

    @router.post("/refresh-config")
    async def refresh_config(authenticated: bool = Depends(require_authentication)) -> dict:
        """
        Refresh dynamic configuration (e.g., after updating vector store ID in Parameter Store).
        """
        new_vs_id = refresh_vector_store_id()
        return {"message": "Config refreshed", "vector_store_id": new_vs_id}

    @router.get("/image/{exam_id}/{rel_path:path}")
    async def image(
        exam_id: str,
        rel_path: str,
        authenticated: bool = Depends(require_authentication),
    ) -> FileResponse:
        """
        Serve image files from the exam directory.
        
        Only allows serving files under the configured exams root.
        """
        # Only allow serving files under the configured exams root:
        #   <exams_root>/<exam_id>/<rel_path>
        candidate = paths.exam_asset_under_root(exams_root, exam_id, rel_path).resolve()
        try:
            candidate.relative_to(exams_root)
        except Exception:
            raise HTTPException(status_code=404, detail="Not found")
        if not candidate.exists() or not candidate.is_file():
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(candidate)

    return router

