# STATUS

## What was built

A local-first Python CLI that generates FINAL FANTASY XIV crafting macros
from recipe and rotation inputs, with step limits and automatic macro
splitting. A fan project by Asdale Dynamics, LLC (not affiliated with Square
Enix).

Components:

- `ffxiv_macro_gen/models.py` — `Step`, `Rotation`, `Recipe`, `Macro` data
  models. Each step renders to `/ac "Action" <t>` plus an optional `/wait`.
- `ffxiv_macro_gen/generator.py` — `MacroGenerator` converts rotations into
  macros, enforcing a configurable per-macro step limit (default 15 command
  lines) and splitting long rotations across numbered parts
  (`Macro Name (1/3)`, etc.).
- `ffxiv_macro_gen/storage.py` — `JSONStore` reads/writes `recipes.json` and
  `rotations.json` in a local data directory (no network, no accounts).
- `ffxiv_macro_gen/exporter.py` — renders macros to game-ready text and
  writes them to a file for pasting into the FFXIV macro editor.
- `ffxiv_macro_gen/cli.py` — argparse CLI: `generate`, `list-rotations`,
  `list-recipes`, `add-rotation`, `add-recipe`. Entry point:
  `ffxiv-macro-gen` (also `python -m ffxiv_macro_gen.cli`).
- `tests/test_macro_generation.py` — 19 tests covering step rendering,
  single-macro generation, macro splitting, edge cases (limit of 1, empty
  rotation), storage round-trips, export, and CLI behavior.
- `data/recipes.json`, `data/rotations.json` — sample FFXIV crafting data.
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC.
- `README.md` — usage guide crediting Asdale Dynamics, LLC.
- `pyproject.toml` — package metadata, console script, pytest config.

## How to run

```bash
# Install
pip install -e .          # or: pip install -e . --break-system-packages

# Generate macros from a stored rotation (prints to stdout)
ffxiv-macro-gen generate "Basic 90 Blacksmith Rotation" --print

# Split a long rotation across macros, writing to a file
ffxiv-macro-gen generate "Long Rotation Example" \
    --steps-per-macro 10 --output out.txt

# List / add data
ffxiv-macro-gen list-rotations
ffxiv-macro-gen list-recipes
ffxiv-macro-gen add-rotation data/rotations.json

# Run tests
pytest
```

## Verification results

- `pytest`: 19 passed.
- CLI smoke-tested: `generate` prints and writes game-ready macro text,
  `list-rotations`/`list-recipes` work, `add-rotation` works, custom
  `--steps-per-macro` splitting works, `--output` writes a file.
- Console script entry point `ffxiv-macro-gen` installed and working.

## Known gaps

- Macro splitting cuts at the command-line level, so a step's `/ac` line
  and its `/wait` line can fall in different macro parts (a leading `/wait`
  in part 2 is valid FFXIV but slightly awkward). A smarter step-aware
  splitter could keep each step's lines together.
- Conditions (`condition` field on steps) are rendered as comments only;
  no in-game conditional logic is emitted.
- No validation that rotation actions match real FFXIV action names.
- No GUI; CLI only. Intended for pasting into the FFXIV macro editor.
