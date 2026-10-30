# FFXIV Crafting Macro Generator CLI

A small, local-first Python CLI that turns crafting recipes and rotations into
FFXIV game-ready macros, with step limits and automatic macro splitting.

A fan project by **Asdale Dynamics, LLC**. Not affiliated with Square Enix or
FINAL FANTASY XIV. For personal use only.

## What it does

FFXIV crafting macros let you run a sequence of crafting actions with one
button. Writing them by hand is tedious, especially when a rotation is longer
than a single macro can hold. This tool:

* Reads recipes and rotations from local JSON files (no accounts, no network).
* Generates `/ac` and `/wait` macro lines from each rotation step.
* Enforces a per-macro step limit (default 15 command lines per macro).
* Splits long rotations across multiple numbered macros automatically.
* Exports plain text you can paste straight into the FFXIV macro editor.

## Install

```bash
git clone <this-repo>
cd ffxiv-crafting-macro-generator-cli
pip install -e .
```

Or just run the module directly:

```bash
python -m ffxiv_macro_gen.cli generate "My Rotation" --print
```

## Usage

Store your rotations in `data/rotations.json` (a `data/recipes.json` file is
also supported for recipe records):

```json
[
  {
    "name": "My Rotation",
    "steps": [
      {"action": "Basic Synthesis", "wait": 0.5},
      {"action": "Basic Touch", "wait": 0.5}
    ]
  }
]
```

Generate macros:

```bash
ffxiv-macro-gen generate "My Rotation" --print
```

Split long rotations across macros (default limit is 15 command lines per
macro):

```bash
ffxiv-macro-gen generate "Long Rotation" --steps-per-macro 10 --output out.txt
```

Other commands:

```bash
ffxiv-macro-gen list-rotations
ffxiv-macro-gen list-recipes
ffxiv-macro-gen add-rotation data/rotations.json
```

## Example output

```
! Macro: My Rotation (1/1)

/ac "Basic Synthesis" <t>
/wait 0.5
/ac "Basic Touch" <t>
/wait 0.5
```

Copy the block between (and including) the `! Macro:` line into the FFXIV
macro editor.

## Testing

```bash
pip install pytest
pytest
```

## Credits

Built by **Asdale Dynamics, LLC** — Dylan Asdale's Indiana LLC focused on
beginner-friendly AI education, practical open-source tools, and small-business
helpers. Learn more at [dylanasdale.github.io](https://dylanasdale.github.io).

This is a fan-made utility for FINAL FANTASY XIV. FINAL FANTASY XIV and
related trademarks are owned by Square Enix. This project is not endorsed or
affiliated with Square Enix.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
