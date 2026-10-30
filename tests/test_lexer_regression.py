from sloperator.lexer import tokenize


def test_comment_newline_advances_line_number():
    tokens = tokenize("— comment\nslop x = 1✨")
    assert [token.line for token in tokens] == [2, 2, 2, 2, 2, 2]
