---
name: create-test-program
description: Add a SlopLang example program and an exact-output test for a given language feature
---

# Create Test Program

Use when asked to cover a SlopLang language feature with an example in `examples/` and an
exact-output test in `tests/test_example_outputs.py`.

## 1. Read the spec

Read `docs/spec.md` and find the sections for the feature. Note its exact syntax, semantics, and
output formatting. The spec is the source of truth: do not invent behavior, and do not rely on
what other languages do. If the spec does not describe the feature, stop and report the gap
instead of guessing.

## 2. Write the example

Check `examples/` first so you do not duplicate an existing program. Then create
`examples/<feature>.slop`, named for the feature with lowercase words (for example,
`string-addition.slop`). Keep it small: demonstrate the feature clearly and avoid unrelated
constructs.

## 3. Capture the exact output

Run the example from the project root:

```bash
uv run sloperator.py examples/<feature>.slop
```

Confirm the exit code is `0` and stderr is empty. Copy the exact stdout, including the trailing
newline produced by the final `hallucinate`. If the output contradicts the spec, fix the example
or report an interpreter bug; never encode incorrect behavior in the test.

## 4. Add the exact-output test

Edit `tests/test_example_outputs.py` and add an entry to `OUTPUTS`, keyed by the example's filename
stem without `.slop`. The value is the exact stdout as a Python string literal:

```python
OUTPUTS = {
    "hello": "hello, slop\n",
    "countdown": "3\n2\n1\nliftoff\n",
}
```

Use `\n` for line breaks and `\t` for tabs. Do not use substring checks, `in` assertions, or normalized whitespace; the test
must compare the entire stdout exactly.

## 5. Verify

Run the new test on its own:

```bash
uv run pytest tests/test_example_outputs.py -k <feature>
```

Then run the full validation from `AGENTS.md`, in order.
Report which checks passed and which failed. Leave the changes uncommitted unless the user
explicitly asks for a commit.
