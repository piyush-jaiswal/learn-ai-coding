import pytest

from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_not_flips_booleans():
    assert run("hallucinate(!✅, !❌, !!✅)✨") == "❌ ✅ ✅\n"


def test_not_binds_tighter_than_equality():
    assert run("hallucinate(!✅ == ❌)✨") == "✅\n"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("hallucinate(!1)✨", "operand of unary '!' must be a boolean, got number"),
        ("hallucinate(!“slop”)✨", "operand of unary '!' must be a boolean, got string"),
    ],
)
def test_not_rejects_non_booleans(source: str, message: str):
    result = run_source(source)

    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr == f"SlopLang runtime error at line 1: {message}\n"
