# Parser

Recursive-descent parser: `parse(tokens)` in `parser.py` turns a token list into the AST nodes in
`ast.py`. `docs/spec.md` is the language source of truth, and its **Grammar** section is the
contract this module implements. Syntax failures raise `SlopSyntaxError`.

## Conventions

### 1. One method per grammar rule

Every rule in the spec's grammar maps to exactly one `Parser` method, and the method is named after
the rule (`topLevel` → `top_level`, `variableDecl` → `var_decl`, `logicOr` → `logic_or`). Each
method consumes the tokens for that rule and returns its node, delegating sub-rules to their own
methods.

- Do not inline one rule into another to save a call; a rule always gets its own method.
- Do not merge sibling rules (for example, keep `logic_or`, `logic_and`, and `equality` separate).
- Do not invent grammar methods for non-rules. Token plumbing (`match`, `check`, `advance`,
  `peek`, `expect`, `error`) and small helpers like `terminator` are fine.
- When the grammar changes, update `docs/spec.md` first, then add or rename the matching method.

### 2. Syntax errors describe the token that was found

An unexpected token must produce a message that says both what was expected and what was found.
Route those errors through `self.error(token, message)`:

```python
raise self.error(self.peek(), "expected ')' after arguments")
# -> "expected ')' after arguments, found '='"
# at EOF -> "expected ')' after arguments, but reached end of file"
```

- Write messages lowercase with no trailing period; quote literal tokens (`'('`, `'✨'`).
- Use `expect` and `primary`'s fallback rather than raising `SlopSyntaxError` directly for
  unexpected tokens; `error()` already appends the found-token clause and handles EOF.
- Reserve direct `raise SlopSyntaxError(...)` for contextual checks where the token is not
  unexpected (duplicate parameter, `clanker` outside the top level, `ship` outside a `clanker`).
  Those messages must still name the offending lexeme.
- Tests assert exact strings, so update `tests/test_parser.py` and `tests/test_errors.py` whenever
  grammar wording changes.
