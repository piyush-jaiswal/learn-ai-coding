import pytest

from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def test_compound_assignment_adds_with_expression_precedence():
    source = """slop n = 2✨
n += 3 * 4✨
hallucinate(n)✨"""
    assert run(source) == "14\n"


def test_compound_assignment_concatenates_strings():
    source = """slop message = “slop”✨
message += “ it”✨
hallucinate(message)✨"""
    assert run(source) == "slop it\n"


def test_compound_assignment_updates_nearest_variable():
    source = """slop score = 1✨
{
    slop score = 2✨
    {
        score += 3✨
    }
    hallucinate(score)✨
}
hallucinate(score)✨"""
    assert run(source) == "5\n1\n"


@pytest.mark.parametrize(
    ("source", "line", "message"),
    [
        ("missing += 1✨", 1, "undefined variable 'missing'"),
        (
            "loadbearing MAX = 10✨\nMAX += 1✨",
            2,
            "cannot assign to loadbearing 'MAX'",
        ),
        (
            "slop n = 1✨\nn += “two”✨",
            2,
            "operands of '+=' must both be numbers or both be strings, got number and string",
        ),
    ],
)
def test_compound_assignment_errors(source: str, line: int, message: str):
    result = run_source(source)
    assert result.stderr == f"SlopLang runtime error at line {line}: {message}\n"
    assert result.exit_code == 1
