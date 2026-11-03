---
name: validate
description: Run Sloperator's tests, formatting check, linter, and type check
---

# Validate

From the project root, run:

1. `uv run pytest`
2. `uv run ruff format --check`
3. `uv run ruff check`
4. `uv run ty check`

Summarize which checks passed and which failed. Report failures before proposing fixes.
