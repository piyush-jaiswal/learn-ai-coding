from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Literal
from sloperator.runner import run_source


def only_expression(source: str) -> Binary:
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    assert isinstance(statement.expression, Binary)
    return statement.expression


def test_multiplication_happens_before_addition():
    expr = only_expression("1 + 2 * 3✨")

    # The root is `+`, and `2 * 3` is nested as its right operand.
    assert expr.operator.type is TokenType.PLUS
    assert isinstance(expr.left, Literal) and expr.left.value == 1
    assert isinstance(expr.right, Binary)
    assert expr.right.operator.type is TokenType.STAR
    assert isinstance(expr.right.left, Literal) and expr.right.left.value == 2
    assert isinstance(expr.right.right, Literal) and expr.right.right.value == 3

    result = run_source("hallucinate(1 + 2 * 3)✨")
    assert result.stderr == ""
    assert result.stdout == "7\n"
