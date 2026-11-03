import pytest

from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("“” + “slop”", "slop"),
        ("“🚀” + “🌟”", "🚀🌟"),
        ("“” + “🧠” + “💩”", "🧠💩"),
    ],
)
def test_plus_concatenates_strings(expression: str, expected: str):
    assert run(f"hallucinate({expression})✨") == f"{expected}\n"
