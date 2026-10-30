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

        Steps are kept together as much as possible: a step's ``/ac`` line and
        its ``/wait`` line stay in the same macro part whenever they fit.
        Macros are split so no macro exceeds ``steps_per_macro`` command lines.
        """
        name = macro_name or rotation.name
        all_parts: list[list[str]] = []
        current: list[str] = []

        for step in rotation.steps:
            step_lines = step.to_macro_lines()
            if not step_lines:
                continue
            if current and len(current) + len(step_lines) > self.steps_per_macro:
                all_parts.append(current)
                current = []
            current.extend(step_lines)

        if current or not all_parts:
            all_parts.append(current)

        macros: list[Macro] = []
        for index, part_lines in enumerate(all_parts, start=1):
            macros.append(
                Macro(
                    name=name,
                    lines=part_lines,
                    part=index,
                    total_parts=len(all_parts),
                )
            )
        return macros

    def generate_recipe_macro(self, recipe_name: str, steps: list[Step]) -> list[Macro]:
        """Convenience: generate macros from an inline step list."""
        rotation = Rotation(name=recipe_name, steps=steps)
        return self.generate(rotation, macro_name=recipe_name)
