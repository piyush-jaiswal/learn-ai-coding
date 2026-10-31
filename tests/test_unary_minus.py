import pytest

from sloperator.runner import run_source


@pytest.mark.parametrize("operand", ["✅", "❌"])
def test_unary_minus_rejects_booleans(operand: str):
    result = run_source(f"hallucinate(-{operand})✨")

    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr == (
        "SlopLang runtime error at line 1: operand of unary '-' must be a number, got boolean\n"
    )
