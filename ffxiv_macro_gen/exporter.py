"""Export macros to game-ready text files."""

from __future__ import annotations

import os
from typing import Iterable

from .models import Macro


def macro_to_text(macro: Macro) -> str:
    """Render a single macro as game-ready text."""
    return macro.to_text()


def rotation_to_text(macros: Iterable[Macro]) -> str:
    """Render all macro parts as one text block, separated by blank lines."""
    blocks = [macro.to_text().rstrip("\n") for macro in macros]
    return "\n\n".join(blocks) + "\n"


def export_macros(macros: Iterable[Macro], output_path: str) -> str:
    """Write macros to a file and return the absolute path written."""
    text = rotation_to_text(macros)
    directory = os.path.dirname(os.path.abspath(output_path))
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return os.path.abspath(output_path)
