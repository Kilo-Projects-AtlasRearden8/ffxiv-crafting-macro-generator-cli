"""Macro generation engine with step limits and macro splitting."""

from __future__ import annotations

from typing import Optional

from .models import Macro, Rotation, Step


class MacroGenerator:
    """Converts rotations into FFXIV game-ready macros."""

    DEFAULT_STEPS_PER_MACRO = 15

    def __init__(self, steps_per_macro: int = DEFAULT_STEPS_PER_MACRO) -> None:
        if steps_per_macro < 1:
            raise ValueError("steps_per_macro must be at least 1")
        self.steps_per_macro = steps_per_macro

    def generate(self, rotation: Rotation, macro_name: Optional[str] = None) -> list[Macro]:
        """Generate macros from a rotation, splitting across the step limit.

        Each step contributes its action line plus an optional /wait line.
        Macros are split so no macro exceeds ``steps_per_macro`` command lines.
        """
        name = macro_name or rotation.name
        all_lines: list[str] = []
        for step in rotation.steps:
            all_lines.extend(step.to_macro_lines())

        parts = self._split_lines(all_lines, self.steps_per_macro)
        macros: list[Macro] = []
        for index, part_lines in enumerate(parts, start=1):
            macros.append(
                Macro(
                    name=name,
                    lines=part_lines,
                    part=index,
                    total_parts=len(parts),
                )
            )
        return macros

    @staticmethod
    def _split_lines(lines: list[str], limit: int) -> list[list[str]]:
        if not lines:
            return [[]]
        chunks: list[list[str]] = []
        for i in range(0, len(lines), limit):
            chunks.append(lines[i : i + limit])
        return chunks

    def generate_recipe_macro(self, recipe_name: str, steps: list[Step]) -> list[Macro]:
        """Convenience: generate macros from an inline step list."""
        rotation = Rotation(name=recipe_name, steps=steps)
        return self.generate(rotation, macro_name=recipe_name)
