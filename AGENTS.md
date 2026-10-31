# AGENTS.md

Sloperator is a tree-walking interpreter for SlopLang, a deliberately absurd language whose
syntax uses `“ ”`, `—`, `✨`, `✅`, and `❌`. `docs/spec.md` is the language source of truth.

## Commands

Always use `uv run`; the project is pinned to Python 3.13 via `.python-version` and has no
runtime dependencies or build step.

```bash
uv run sloperator.py examples/hello.slop      # run a program
uv run sloperator.py --check examples/hello.slop  # lex + parse only, no execution
uv run playground/server.py                   # web playground on localhost:8080
```

Validation — all four must pass, in this order:

```bash
uv run pytest
uv run ruff format --check
uv run ruff check
uv run ty check
```

- Single test: `uv run pytest tests/test_errors.py::test_error_message`
- The `validate` skill (`.agents/skills/validate/SKILL.md`) omits `ty check`; run the four commands above.

## Architecture

- `sloperator.py` is the CLI: read file → `tokenize` → `parse` → `Interpreter`. Exit codes: `0`
  success, `1` SlopLang error, `2` usage or unreadable file.
- `sloperator/runner.py` is the shared entrypoint: `run_program` for streaming output,
  `run_source` for in-process tests (`RunResult` with stdout/stderr/exit code). Most tests use
  `run_source`.
- `--check` calls `validate_source` (lex/parse only), so valid syntax with runtime failures still
  reports `Syntax OK`.
- Errors are `SlopError` subclasses; the exact contract is
  `SlopLang <lexical|syntax|runtime> error at line N: message` on stderr. Tests assert exact
  strings, so update the matching test when changing wording.
- Python tracebacks must never escape. The interpreter converts `RecursionError` to a runtime
  error, and `runner.py` raises Python's recursion limit to 20,000. User call depth is capped at
  `MAX_CALL_DEPTH = 500` in `sloperator/evaluator/interpreter.py`.
- Every brace block opens a scope. Functions are first-class values, but `clanker` declarations
  must appear before the first call. There are no nested functions.

## Repo-specific gotchas

- Use the real Unicode characters in `.slop` files and tests. Straight quotes, `;`, `//`, and the
  en dash `–` are lexical errors with deliberate messages.
- `tests/test_examples.py` auto-discovers `examples/*.slop`; every example must exit cleanly and
  print non-empty stdout. Adding an example adds a test.
- Keep language changes in `docs/spec.md`; the README is intentionally a condensed summary.
- Known mismatch: `ralph` currently executes its body once before checking the condition, contrary
  to the spec. Do not assume condition-first behavior when writing loop tests; check the actual
  interpreter.
- The playground shells out to `sloperator.py` per request with a 5-second timeout and appends JSON
  runs to `logs/runs.log`; `logs/` is gitignored and watcher-ignored.
- `opencode.jsonc` intentionally denies reading `*.env` / `*.env.*`; do not try to bypass it.
- `.opencode/plugins/*.ts` provide the `run_slop` and `commit_message` tools and run under Bun.
  If you change plugin dependencies, run `bun install` in `.opencode/`.
- Commit messages: boot.dev lesson changes use
  `Ch <chapter>.<lesson> - <Lesson Title>: <summary>`; other changes use one-liners such as
  `fix: ...`, `feat: ...`, or `Chore: ...`. The `commit_message` tool builds the lesson form.
