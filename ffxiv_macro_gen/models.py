"""Data models for FFXIV crafting macro generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Step:
    """A single action in a crafting rotation."""

    action: str
    wait: float = 0.0
    condition: Optional[str] = None
    note: Optional[str] = None

    def to_macro_lines(self) -> list[str]:
        """Render this step as FFXIV macro command lines."""
        lines: list[str] = []
        if self.condition:
            lines.append(f'# {self.condition}: {self.action}')
        lines.append(f'/ac "{self.action}" <t>')
        if self.wait and self.wait > 0:
            lines.append(f"/wait {self.wait:g}")
        return lines


@dataclass
class Rotation:
    """A crafting rotation: an ordered list of steps."""

    name: str
    steps: list[Step] = field(default_factory=list)

    def add_step(self, step: Step) -> None:
        self.steps.append(step)


@dataclass
class Recipe:
    """A craftable item recipe."""

    id: str
    name: str
    level: int = 1
    job: str = "Any"
    durability: int = 80
    max_quality: int = 0


@dataclass
class Macro:
    """A generated FFXIV macro, ready to paste into the game."""

    name: str
    lines: list[str]
    part: int = 1
    total_parts: int = 1

    def header(self) -> str:
        if self.total_parts > 1:
            return f"! Macro: {self.name} ({self.part}/{self.total_parts})"
        return f"! Macro: {self.name}"

    def to_text(self) -> str:
        lines = [self.header(), ""]
        lines.extend(self.lines)
        return "\n".join(lines) + "\n"
