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


def test_nested_calls_can_appear_in_multiple_arguments():
    expr = only_expression("outer(inner(1), other(2, 3))✨")
    assert isinstance(expr, Call)
    assert [argument.callee.name.lexeme for argument in expr.arguments] == ["inner", "other"]
    assert all(isinstance(argument, Call) for argument in expr.arguments)


def test_calls_nest_to_arbitrary_depth():
    expr = only_expression("a(b(c(1)))✨")
    assert isinstance(expr, Call)
    inner = expr.arguments[0]
    assert isinstance(inner, Call) and inner.callee.name.lexeme == "b"
    innermost = inner.arguments[0]
    assert isinstance(innermost, Call) and innermost.callee.name.lexeme == "c"
    assert isinstance(innermost.arguments[0], Literal)
    assert innermost.arguments[0].value == 1


def test_nested_call_inside_a_larger_argument_expression():
    expr = only_expression("hallucinate(add(1, 2) + 3)✨")
    assert isinstance(expr, Call)
    (argument,) = expr.arguments
    assert isinstance(argument, Binary)
    assert isinstance(argument.left, Call) and argument.left.callee.name.lexeme == "add"
    assert isinstance(argument.right, Literal) and argument.right.value == 3
