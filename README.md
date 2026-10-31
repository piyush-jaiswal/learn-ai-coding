# Sloperator

A tree-walking interpreter for SlopLang, written in Python. See **[docs/spec.md](docs/spec.md)** for the language specification.

## Quick Start

```bash
uv run sloperator.py examples/fib.slop   # run a program
uv run playground/server.py              # playground at localhost:8080
```

## Validation

```bash
uv run pytest              # tests
uv run ruff format --check # formatting
uv run ruff check          # linting
uv run ty check            # type checking
```

## Example

```slop
slop count = 0✨
ralph count < 3 {
    hallucinate(“count”, count)✨
    count = count + 1✨
}
```

Prints `count 0`, `count 1`, `count 2`.

## Layout

| Path | What it is |
| --- | --- |
| `sloperator.py` | CLI entrypoint |
| `sloperator/` | `lexer/`, `parser/`, `evaluator/`, and `runner.py` |
| `docs/spec.md` | Language specification |
| `examples/`, `tests/`, `playground/` | Examples, pytest suite, and web playground |
