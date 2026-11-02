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

Single test: `uv run pytest tests/test_errors.py::test_error_message`. The `validate` skill
(`.agents/skills/validate/SKILL.md`) omits `ty check`; run the four commands above.

## When to add regression tests

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

## Language behavior

[docs/spec.md](docs/spec.md) is the source of truth for SlopLang syntax, semantics, and error
messages. Read it before changing or testing language behavior, and update it with any language
change; the README is intentionally only a condensed summary.

Python tracebacks must never escape: `runner.py` raises Python's recursion limit to 20,000, and the
interpreter converts `RecursionError` into a runtime error. The user-facing call-depth cap is 500
(see the spec).

Known mismatch: `ralph` executes its body once before checking the condition (a do-while), although
the spec says condition-first. Check the interpreter rather than assuming spec behavior when
writing loop tests.
