from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Assign, Binary, ExprStmt, Literal


def parse_source(source: str):
    return parse(tokenize(source))


def test_plus_equals_is_a_single_token():
    tokens = tokenize("x += 1✨")
    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.PLUS_EQUAL,
        TokenType.NUMBER,
        TokenType.SPARKLES,
        TokenType.EOF,
    ]
    assert tokens[1].lexeme == "+="
    assert tokens[1].line == 1


def test_compound_assignment_is_a_statement():
    (statement,) = parse_source("x += 1✨")
    assert isinstance(statement, Assign)
    assert statement.name.lexeme == "x"
    assert statement.operator.type is TokenType.PLUS_EQUAL
    assert isinstance(statement.value, Literal) and statement.value.value == 1


def test_compound_assignment_value_is_a_full_expression():
    (statement,) = parse_source("x += 1 + 2 * 3✨")
    assert isinstance(statement, Assign)
    value = statement.value
    assert isinstance(value, Binary) and value.operator.type is TokenType.PLUS
    assert isinstance(value.right, Binary) and value.right.operator.type is TokenType.STAR


def test_plain_plus_is_still_an_expression():
    (statement,) = parse_source("x + 1✨")
    assert isinstance(statement, ExprStmt)
    assert isinstance(statement.expression, Binary)
    assert statement.expression.operator.type is TokenType.PLUS
