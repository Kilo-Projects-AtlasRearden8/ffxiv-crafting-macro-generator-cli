"""Local JSON storage for recipes and rotations."""

from __future__ import annotations

import json
import os
from typing import Optional

from .models import Recipe, Rotation, Step


class JSONStore:
    """Simple file-based JSON storage for recipes and rotations."""

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    # ------------------------------------------------------------------ paths
    def _recipes_path(self) -> str:
        return os.path.join(self.data_dir, "recipes.json")

    def _rotations_path(self) -> str:
        return os.path.join(self.data_dir, "rotations.json")

    # --------------------------------------------------------------- recipes
    def load_recipes(self) -> list[Recipe]:
        return self._load_list(self._recipes_path(), self._dict_to_recipe)

    def save_recipes(self, recipes: list[Recipe]) -> None:
        self._save_list(self._recipes_path(), recipes, self._recipe_to_dict)

    def add_recipe(self, recipe: Recipe) -> None:
        recipes = self.load_recipes()
        if any(r.id == recipe.id for r in recipes):
            raise ValueError(f"Recipe with id '{recipe.id}' already exists")
        recipes.append(recipe)
        self.save_recipes(recipes)

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        for recipe in self.load_recipes():
            if recipe.id == recipe_id:
                return recipe
        return None

    # ------------------------------------------------------------ rotations
    def load_rotations(self) -> list[Rotation]:
        return self._load_list(self._rotations_path(), self._dict_to_rotation)

    def save_rotations(self, rotations: list[Rotation]) -> None:
        self._save_list(self._rotations_path(), rotations, self._rotation_to_dict)

    def add_rotation(self, rotation: Rotation) -> None:
        rotations = self.load_rotations()
        if any(r.name == rotation.name for r in rotations):
            raise ValueError(f"Rotation with name '{rotation.name}' already exists")
        rotations.append(rotation)
        self.save_rotations(rotations)

    def get_rotation(self, name: str) -> Optional[Rotation]:
        for rotation in self.load_rotations():
            if rotation.name == name:
                return rotation
        return None

    # ----------------------------------------------------------- serialization
    @staticmethod
    def _load_list(path: str, converter) -> list:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            return []
        return [converter(item) for item in data]

    @staticmethod
    def _save_list(path: str, items: list, to_dict) -> None:
        serializable = [to_dict(item) for item in items]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(serializable, handle, indent=2)
            handle.write("\n")

    @staticmethod
    def _recipe_to_dict(recipe: Recipe) -> dict:
        return {
            "id": recipe.id,
            "name": recipe.name,
            "level": recipe.level,
            "job": recipe.job,
            "durability": recipe.durability,
            "max_quality": recipe.max_quality,
        }

    @staticmethod
    def _dict_to_recipe(data: dict) -> Recipe:
        return Recipe(
            id=str(data["id"]),
            name=str(data["name"]),
            level=int(data.get("level", 1)),
            job=str(data.get("job", "Any")),
            durability=int(data.get("durability", 80)),
            max_quality=int(data.get("max_quality", 0)),
        )

    @staticmethod
    def _rotation_to_dict(rotation: Rotation) -> dict:
        return {
            "name": rotation.name,
            "steps": [
                {
                    "action": step.action,
                    "wait": step.wait,
                    "condition": step.condition,
                    "note": step.note,
                }
                for step in rotation.steps
            ],
        }

    @staticmethod
    def _dict_to_rotation(data: dict) -> Rotation:
        steps = [
            Step(
                action=str(item.get("action", "")),
                wait=float(item.get("wait", 0.0)),
                condition=item.get("condition"),
                note=item.get("note"),
            )
            for item in data.get("steps", [])
        ]
        return Rotation(name=str(data["name"]), steps=steps)
