import pytest

from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Literal
from sloperator.runner import run_source


def only_expression(source: str) -> Binary:
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    assert isinstance(statement.expression, Binary)
    return statement.expression


def test_comparison_binds_tighter_than_equality():
    expr = only_expression("1 < 2 == ✅✨")

    # The root is `==`, and `1 < 2` is nested as its left operand.
    assert expr.operator.type is TokenType.EQUAL_EQUAL
    assert isinstance(expr.left, Binary)
    assert expr.left.operator.type is TokenType.LESS
    assert isinstance(expr.right, Literal) and expr.right.value is True


def test_equality_binds_looser_than_comparison():
    expr = only_expression("1 == 1 < 2✨")

    # The root is `==`, and `1 < 2` is nested as its right operand.
    assert expr.operator.type is TokenType.EQUAL_EQUAL
    assert isinstance(expr.left, Literal) and expr.left.value == 1
    assert isinstance(expr.right, Binary)
    assert expr.right.operator.type is TokenType.LESS


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 < 2 == ✅", "✅"),
        ("1 == 1 < 2", "❌"),
        ("1 < 2 != ❌", "✅"),
        ("✅ && 1 == 1", "✅"),
        ("1 < 2 && 2 < 3", "✅"),
    ],
)
def test_comparison_and_equality_precedence(expression: str, expected: str):
    result = run_source(f"hallucinate({expression})✨")

    assert result.stderr == ""
    assert result.stdout == f"{expected}\n"
