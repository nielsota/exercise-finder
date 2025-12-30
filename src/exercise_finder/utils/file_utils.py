"""File system utilities."""
from __future__ import annotations

from pathlib import Path

from exercise_finder.constants import IGNORED_FILES


def get_files(
    directory: Path,
    pattern: str = "*",
    with_ignore: bool = True,
) -> list[Path]:
    """
    Get files from a directory, optionally filtering out ignored system files.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (default: "*" for all files)
        with_ignore: If True, filter out system files from IGNORED_FILES
    
    Returns:
        List of Path objects for files matching the pattern
    
    Example:
        >>> from pathlib import Path
        >>> files = get_files(Path("pages"), pattern="*.png")
        >>> # Returns only .png files, excluding .DS_Store etc.
    """
    files = [f for f in directory.glob(pattern) if f.is_file()]
    
    if with_ignore:
        files = [f for f in files if f.name not in IGNORED_FILES]
    
    return files

