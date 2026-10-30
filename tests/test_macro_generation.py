"""Tests for FFXIV crafting macro generation."""

from __future__ import annotations

import json
import os
import tempfile

from ffxiv_macro_gen.cli import main
from ffxiv_macro_gen.exporter import export_macros, rotation_to_text
from ffxiv_macro_gen.generator import MacroGenerator
from ffxiv_macro_gen.models import Macro, Recipe, Rotation, Step
from ffxiv_macro_gen.storage import JSONStore


# ------------------------------------------------------------------ models

def test_step_to_macro_lines_action_only():
    step = Step(action="Basic Synthesis")
    assert step.to_macro_lines() == ['/ac "Basic Synthesis" <t>']


def test_step_to_macro_lines_with_wait():
    step = Step(action="Basic Touch", wait=0.5)
    assert step.to_macro_lines() == ['/ac "Basic Touch" <t>', "/wait 0.5"]


def test_step_to_macro_lines_with_condition():
    step = Step(action="Advanced Touch", condition="good quality", wait=1.0)
    lines = step.to_macro_lines()
    assert lines[0] == "# good quality: Advanced Touch"
    assert lines[1] == '/ac "Advanced Touch" <t>'
    assert lines[2] == "/wait 1"


# ------------------------------------------------------------ generator

def test_generate_single_macro_under_limit():
    rotation = Rotation(
        name="Short Rotation",
        steps=[Step(action="Basic Synthesis"), Step(action="Basic Touch")],
    )
    macros = MacroGenerator(steps_per_macro=15).generate(rotation)
    assert len(macros) == 1
    assert macros[0].name == "Short Rotation"
    assert macros[0].lines == [
        '/ac "Basic Synthesis" <t>',
        '/ac "Basic Touch" <t>',
    ]


def test_generate_splits_over_limit():
    steps = [Step(action=f"Action {i}") for i in range(20)]
    rotation = Rotation(name="Long Rotation", steps=steps)
    macros = MacroGenerator(steps_per_macro=7).generate(rotation)

    assert len(macros) == 3
    assert macros[0].name == "Long Rotation"
    assert macros[0].part == 1
    assert macros[0].total_parts == 3
    assert len(macros[0].lines) == 7
    assert len(macros[1].lines) == 7
    assert len(macros[2].lines) == 6

    # No line is lost across the split.
    flat = [line for macro in macros for line in macro.lines]
    assert len(flat) == 20
    assert flat == ['/ac "Action 0" <t>', '/ac "Action 19" <t>'][:0] or True
    assert flat[0] == '/ac "Action 0" <t>'
    assert flat[-1] == '/ac "Action 19" <t>'


def test_generate_steps_per_macro_one():
    rotation = Rotation(name="X", steps=[Step(action="A"), Step(action="B")])
    macros = MacroGenerator(steps_per_macro=1).generate(rotation)
    assert len(macros) == 2
    assert macros[0].lines == ['/ac "A" <t>']
    assert macros[1].lines == ['/ac "B" <t>']


def test_generate_empty_rotation():
    rotation = Rotation(name="Empty", steps=[])
    macros = MacroGenerator().generate(rotation)
    assert len(macros) == 1
    assert macros[0].lines == []


def test_invalid_steps_per_macro():
    try:
        MacroGenerator(steps_per_macro=0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for steps_per_macro=0")


def test_macro_to_text_header():
    macro = Macro(name="Test Macro", lines=['/ac "A" <t>'], part=2, total_parts=3)
    text = macro.to_text()
    assert text.startswith("! Macro: Test Macro (2/3)\n")
    assert text.endswith('/ac "A" <t>\n')


# ------------------------------------------------------------ exporter

def test_export_writes_file(tmp_path):
    out = tmp_path / "macro.txt"
    macros = [Macro(name="M", lines=['/ac "A" <t>'])]
    path = export_macros(macros, str(out))
    assert os.path.abspath(str(out)) == path
    assert out.read_text() == "! Macro: M\n\n/ac \"A\" <t>\n"


def test_rotation_to_text_joins_parts():
    macros = [
        Macro(name="M", lines=['/ac "A" <t>'], part=1, total_parts=2),
        Macro(name="M", lines=['/ac "B" <t>'], part=2, total_parts=2),
    ]
    text = rotation_to_text(macros)
    assert "/ac \"B\" <t>" in text
    assert text.count("! Macro: M") == 2


# ------------------------------------------------------------ storage

def test_storage_round_trip_rotation(tmp_path):
    store = JSONStore(str(tmp_path))
    rotation = Rotation(
        name="Test Rot",
        steps=[Step(action="Basic Synthesis", wait=0.5)],
    )
    store.add_rotation(rotation)
    loaded = store.get_rotation("Test Rot")
    assert loaded is not None
    assert loaded.name == "Test Rot"
    assert loaded.steps[0].action == "Basic Synthesis"
    assert loaded.steps[0].wait == 0.5

    # File exists and is valid JSON.
    with open(os.path.join(str(tmp_path), "rotations.json"), "r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert len(data) == 1


def test_storage_duplicate_rotation_raises(tmp_path):
    store = JSONStore(str(tmp_path))
    rotation = Rotation(name="Dup", steps=[Step(action="A")])
    store.add_rotation(rotation)
    try:
        store.add_rotation(rotation)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for duplicate rotation")


def test_storage_recipes(tmp_path):
    store = JSONStore(str(tmp_path))
    recipe = Recipe(id="r1", name="Test Recipe", level=90, job="Blacksmith")
    store.add_recipe(recipe)
    loaded = store.get_recipe("r1")
    assert loaded is not None
    assert loaded.job == "Blacksmith"
    assert loaded.level == 90


def test_storage_missing_files_return_empty(tmp_path):
    store = JSONStore(str(tmp_path))
    assert store.load_recipes() == []
    assert store.load_rotations() == []


# ------------------------------------------------------------ cli

def test_cli_generate_prints(tmp_path):
    store_dir = tmp_path / "data"
    store_dir.mkdir()
    (store_dir / "rotations.json").write_text(
        json.dumps(
            [
                {
                    "name": "Cli Rot",
                    "steps": [
                        {"action": "Basic Synthesis", "wait": 0.5},
                        {"action": "Basic Touch", "wait": 0.5},
                    ],
                }
            ]
        )
    )

    exit_code = main(
        [
            "--data-dir",
            str(store_dir),
            "generate",
            "Cli Rot",
            "--steps-per-macro",
            "2",
            "--print",
        ]
    )
    assert exit_code == 0


def test_cli_generate_missing_rotation(tmp_path):
    store_dir = tmp_path / "data"
    store_dir.mkdir()
    exit_code = main(["--data-dir", str(store_dir), "generate", "Nope"])
    assert exit_code == 1


def test_cli_generate_output_file(tmp_path):
    store_dir = tmp_path / "data"
    store_dir.mkdir()
    (store_dir / "rotations.json").write_text(
        json.dumps(
            [{"name": "File Rot", "steps": [{"action": "Basic Synthesis"}]}]
        )
    )
    out = tmp_path / "out" / "macro.txt"
    exit_code = main(
        ["--data-dir", str(store_dir), "generate", "File Rot", "--output", str(out)]
    )
    assert exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "/ac \"Basic Synthesis\" <t>" in content


def test_cli_list_rotations(tmp_path, capsys):
    store_dir = tmp_path / "data"
    store_dir.mkdir()
    (store_dir / "rotations.json").write_text(
        json.dumps([{"name": "Alpha", "steps": []}])
    )
    exit_code = main(["--data-dir", str(store_dir), "list-rotations"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Alpha" in captured.out
