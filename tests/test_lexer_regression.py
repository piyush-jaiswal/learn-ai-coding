from sloperator.lexer import TokenType, tokenize


def test_comment_newline_advances_line_number():
    tokens = tokenize("— comment\nslop x = 1✨")
    assert [token.line for token in tokens] == [2, 2, 2, 2, 2, 2]


def test_identifiers_allow_digits_after_the_first_character():
    tokens = tokenize("score2 = score2 + parse2(a1)✨")
    assert [(token.type, token.lexeme) for token in tokens] == [
        (TokenType.IDENTIFIER, "score2"),
        (TokenType.EQUAL, "="),
        (TokenType.IDENTIFIER, "score2"),
        (TokenType.PLUS, "+"),
        (TokenType.IDENTIFIER, "parse2"),
        (TokenType.LEFT_PAREN, "("),
        (TokenType.IDENTIFIER, "a1"),
        (TokenType.RIGHT_PAREN, ")"),
        (TokenType.SPARKLES, "✨"),
        (TokenType.EOF, ""),
    ]


def test_identifiers_cannot_start_with_a_digit():
    assert [token.type for token in tokenize("2score")] == [
        TokenType.NUMBER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
