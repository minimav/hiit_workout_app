"""Miscellaneous utils."""
from pathlib import Path
import sys


def get_path_to_file(path: Path) -> Path:
    """Get path to file dealing with installed case."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / path  # type: ignore
    else:
        return path
