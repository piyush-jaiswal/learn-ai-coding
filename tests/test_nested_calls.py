from sloperator.lexer import tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, Call, ExprStmt, Literal, Variable


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def test_nested_call_is_an_argument_to_outer_call():
    expr = only_expression("hallucinate(add(1, 2))✨")
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Variable) and expr.callee.name.lexeme == "hallucinate"
    (argument,) = expr.arguments
    assert isinstance(argument, Call)
    assert isinstance(argument.callee, Variable) and argument.callee.name.lexeme == "add"
    assert [type(arg) for arg in argument.arguments] == [Literal, Literal]
    assert [arg.value for arg in argument.arguments] == [1, 2]


def test_nested_call_inside_a_larger_argument_expression():
    expr = only_expression("hallucinate(add(1, 2) + 3)✨")
    assert isinstance(expr, Call)
    (argument,) = expr.arguments
    assert isinstance(argument, Binary)
    assert isinstance(argument.left, Call) and argument.left.callee.name.lexeme == "add"
    assert isinstance(argument.right, Literal) and argument.right.value == 3
