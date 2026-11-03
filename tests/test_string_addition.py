import pytest

from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("“ab” + “cd”", "abcd"),
        ("“” + “”", ""),
        ("“” + “slop”", "slop"),
        ("“slop” + “”", "slop"),
        ("“🚀” + “🌟”", "🚀🌟"),
        ("“” + “🧠” + “💩”", "🧠💩"),
        ("“a” + “🚀” + “”", "a🚀"),
    ],
)
def test_plus_concatenates_strings(expression: str, expected: str):
    assert run(f"hallucinate({expression})✨") == f"{expected}\n"


def test_hallucinate_prints_concatenated_strings():
    source = "hallucinate(“ab” + “cd”, “🚀” + “”, “” + “🌟”, “” + “”)✨"
    assert run(source) == "abcd 🚀 🌟 \n"
