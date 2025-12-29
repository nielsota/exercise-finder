"""Exercise Finder CLI - Main entry point."""
from __future__ import annotations

import typer  # type: ignore[import-not-found]

from exercise_finder.cli.modules import ui, extract, format, vectorstore


app = typer.Typer(
    name="exercise-finder",
    help="Exercise Finder CLI - Manage exam questions and vector stores",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(ui.app, name="ui")
app.add_typer(extract.app, name="extract")
app.add_typer(format.app, name="format")
app.add_typer(vectorstore.app, name="vectorstore")


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
