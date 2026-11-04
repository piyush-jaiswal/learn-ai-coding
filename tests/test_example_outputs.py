"""Exact expected stdout for examples that document a language feature."""

from pathlib import Path

import pytest

from sloperator.runner import run_source

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

# Example filename stem -> exact stdout, including the newline from each hallucinate.
OUTPUTS = {
    "hello": "hello, slop\n",
    "countdown": "3\n2\n1\nliftoff\n",
    "equality": "✅\n❌\n❌\n",
    "short-circuit": "❌\n✅\n",
}


@pytest.mark.parametrize(("name", "expected"), OUTPUTS.items(), ids=OUTPUTS.keys())
def test_example_output(name: str, expected: str):
    source = (EXAMPLES / f"{name}.slop").read_text(encoding="utf-8")
    result = run_source(source)
    assert result.stderr == ""
    assert result.exit_code == 0
    assert result.stdout == expected
