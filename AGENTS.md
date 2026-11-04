# AGENTS.md

Sloperator is a tree-walking interpreter for SlopLang, a deliberately absurd language whose
syntax uses `“ ”`, `—`, `✨`, `✅`, and `❌`.

## Project layout

```text
sloperator.py          CLI: read file → tokenize → parse → Interpreter
sloperator/lexer/      tokenizer
sloperator/parser/     AST and parser
sloperator/evaluator/  interpreter, environments, values
sloperator/runner.py   shared entrypoint: run_program (streaming), run_source (tests)
tests/                 pytest suite; most tests call run_source
examples/              sample .slop programs, auto-discovered by tests
playground/            web playground on localhost:8080
docs/spec.md           language source of truth
```

Python 3.13 is pinned via `.python-version`, with no runtime dependencies or build step. Always
use `uv run`:

```bash
uv run sloperator.py examples/hello.slop            # run a program
uv run sloperator.py --check examples/hello.slop    # lex + parse only
uv run playground/server.py                         # web playground
```

## Validation

All four must pass, in this order:

```bash
uv run pytest
uv run ruff format --check
uv run ruff check
uv run ty check
```

Single test: `uv run pytest tests/test_errors.py::test_error_message`. Comparison precedence
tests: `uv run pytest tests/test_comparisons.py`. The `validate` skill
(`.agents/skills/validate/SKILL.md`) omits `ty check`; run the four commands above.

## When to add regression tests

Tests are cheap to write but not free to maintain. Keep tests for behavior the spec intends to
keep, and skip tests for behavior likely to be respecified.

Add:

- **Every bug fix.** Add a test that fails before the fix and passes after, named for the bug.
- **Every language behavior change.** Cover new or changed syntax, evaluation, scoping, and
  built-ins, including the exact `SlopLang <lexical|syntax|runtime> error at line N: message`
  text — tests assert exact strings.
- **Every CLI change.** Cover flags, output, and exit codes (`0` success, `1` SlopLang error, `2`
  usage or unreadable file).
- **Lexer edge cases,** especially Unicode and near-miss characters, belong in
  `tests/test_lexer_regression.py`.
- **New `examples/*.slop` files** are picked up automatically by `tests/test_examples.py`, which
  requires clean exit and non-empty stdout. Still add a focused test when the example covers new
  behavior.

Avoid:

- **Redundant variants.** One test per behavior and code path. Parametrize when cases exercise
  different branches (signs, types, escapes), not when they differ only in literal values.
- **Re-testing a unit through a higher-level entry point.** Operator, comparison, and precedence
  rules belong in `tests/test_evaluator.py` and `tests/test_precedence.py`; don't repeat them from
  loop, example, or CLI tests.
- **Pinning incidental output.** `tests/test_examples.py` already requires examples to run cleanly
  with non-empty stdout — don't assert their exact text. Same for playground copy, README slogans,
  and other strings likely to change.

## Language behavior

[docs/spec.md](docs/spec.md) is the source of truth for SlopLang syntax, semantics, and error
messages. Read it before changing or testing language behavior, and update it with any language
change; the README is intentionally only a condensed summary.

Python tracebacks must never escape: `runner.py` raises Python's recursion limit to 20,000, and the
interpreter converts `RecursionError` into a runtime error. The user-facing call-depth cap is 500
(see the spec).

## Ground rules

When the user asks you to undo an AI-written change and the mistake is not obvious or already
covered here, suggest an `AGENTS.md` edit that would prevent the same problem. Always ask
permission before making the edit.

Never run `git commit` unless the user explicitly asks for a commit in that same request. Requests
like "fix this", "add that", or "revert it" are not permission to commit. Make the edits, run
validation, report the result, and leave the work uncommitted. This applies to every agent and
subagent. When a commit is requested, stage the changes with `git add` and commit through the
`commit_changes` tool; direct `git commit` is denied by permissions.