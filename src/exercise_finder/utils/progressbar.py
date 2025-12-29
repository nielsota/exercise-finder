"""Progress bar utilities using Rich."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from rich.progress import (  # type: ignore[import-not-found]
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TaskID,
)


@contextmanager
def create_progress_bar(description: str, total: int) -> Iterator[tuple[Progress, TaskID]]:
    """
    Create a progress bar for long-running operations.
    
    Args:
        description: Initial description text
        total: Total number of items to process
        
    Yields:
        (progress, task_id) tuple for updating progress
        
    Example:
        >>> with create_progress_bar("Processing files", total=10) as (progress, task):
        ...     for i, file in enumerate(files):
        ...         # Do work
        ...         process_file(file)
        ...         # Update progress
        ...         progress.update(task, advance=1, description=f"✓ Processed {file}")
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(description, total=total)
        yield progress, task

