"""Progress bar utilities using Rich."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from loguru import logger
from rich.console import Console  # type: ignore[import-not-found]
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
    
    Integrates with loguru so log messages appear above the progress bar
    without disrupting the display.
    
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
    # Create Rich console for the progress bar
    console = Console()
    
    # Temporarily redirect loguru to Rich's console during progress bar display
    handler_id = logger.add(
        lambda msg: console.print(msg, end=""),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
    )
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(description, total=total)
            yield progress, task
    finally:
        # Remove the temporary handler when done
        logger.remove(handler_id)

