"""Web UI command."""
from __future__ import annotations

from pathlib import Path

import typer  # type: ignore[import-not-found]
import uvicorn  # type: ignore[import-not-found]

from exercise_finder.web.app import create_app
import exercise_finder.paths as paths


app = typer.Typer(help="Web UI commands")


@app.command("start")
def start_ui(
    exams_root: Path = typer.Option(
        paths.questions_images_root(),
        "--exams-root",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Folder that contains multiple exam folders, e.g. data/questions-images",
    ),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    """Start a local web UI (best/randomize/redo + image display)."""
    web_app = create_app(exams_root=exams_root)
    uvicorn.run(web_app, host=host, port=port)

