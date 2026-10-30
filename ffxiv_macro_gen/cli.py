"""Command-line interface for the FFXIV crafting macro generator."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from .exporter import export_macros, rotation_to_text
from .generator import MacroGenerator
from .models import Recipe, Rotation, Step
from .storage import JSONStore


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ffxiv-macro-gen",
        description="Generate FFXIV crafting macros from recipes and rotations.",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory holding recipes.json and rotations.json (default: data)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate macros from a stored rotation")
    gen.add_argument("rotation", help="Name of the rotation to generate from")
    gen.add_argument("--name", help="Output macro name (default: rotation name)")
    gen.add_argument(
        "--steps-per-macro",
        type=int,
        default=15,
        help="Maximum command lines per macro (default: 15)",
    )
    gen.add_argument("--output", help="Write exported macro text to this file")
    gen.add_argument(
        "--print",
        action="store_true",
        help="Print the generated macro text to stdout",
    )

    list_rot = sub.add_parser("list-rotations", help="List stored rotations")
    list_rec = sub.add_parser("list-recipes", help="List stored recipes")

    add_rot = sub.add_parser("add-rotation", help="Add a rotation from a JSON file")
    add_rot.add_argument("file", help="JSON file describing the rotation")

    add_rec = sub.add_parser("add-recipe", help="Add a recipe from a JSON file")
    add_rec.add_argument("file", help="JSON file describing the recipe")

    return parser


def _cmd_generate(args: argparse.Namespace, store: JSONStore) -> int:
    rotation = store.get_rotation(args.rotation)
    if rotation is None:
        print(f"error: rotation '{args.rotation}' not found", file=sys.stderr)
        return 1

    generator = MacroGenerator(steps_per_macro=args.steps_per_macro)
    macros = generator.generate(rotation, macro_name=args.name)

    text = rotation_to_text(macros)
    if args.print:
        print(text, end="")
    if args.output:
        path = export_macros(macros, args.output)
        print(f"wrote {len(macros)} macro part(s) to {path}")

    print(
        f"generated {len(macros)} macro part(s) for rotation '{args.rotation}' "
        f"({args.steps_per_macro} steps/macro limit)"
    )
    return 0


def _cmd_list(items: list, label: str) -> int:
    if not items:
        print(f"No {label} stored yet.")
        return 0
    print(f"Stored {label}:")
    for item in items:
        print(f" - {getattr(item, 'name', getattr(item, 'id', item))}")
    return 0


def _cmd_add(path: str, loader, adder, label: str) -> int:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        for entry in data:
            item = loader(entry)
            try:
                adder(item)
            except ValueError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1
        print(f"added {len(data)} {label}(s) from {path}")
    else:
        item = loader(data)
        try:
            adder(item)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"added {label}: {getattr(item, 'name', getattr(item, 'id', item))}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    store = JSONStore(args.data_dir)

    if args.command == "generate":
        return _cmd_generate(args, store)
    if args.command == "list-rotations":
        return _cmd_list(store.load_rotations(), "rotations")
    if args.command == "list-recipes":
        return _cmd_list(store.load_recipes(), "recipes")
    if args.command == "add-rotation":
        return _cmd_add(
            args.file,
            lambda d: _rotation_from_dict(d),
            store.add_rotation,
            "rotation",
        )
    if args.command == "add-recipe":
        return _cmd_add(
            args.file,
            lambda d: _recipe_from_dict(d),
            store.add_recipe,
            "recipe",
        )
    parser.print_help(sys.stderr)
    return 2


def _rotation_from_dict(data: dict) -> Rotation:
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


def _recipe_from_dict(data: dict) -> Recipe:
    return Recipe(
        id=str(data["id"]),
        name=str(data["name"]),
        level=int(data.get("level", 1)),
        job=str(data.get("job", "Any")),
        durability=int(data.get("durability", 80)),
        max_quality=int(data.get("max_quality", 0)),
    )


if __name__ == "__main__":
    raise SystemExit(main())
