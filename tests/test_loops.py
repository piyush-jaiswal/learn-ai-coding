import pytest

from sloperator.runner import run_source


def run(source: str) -> str:
    result = run_source(source)
    assert result.stderr == "", result.stderr
    return result.stdout


def fails(source: str) -> str:
    result = run_source(source)
    assert result.exit_code == 1
    return result.stderr.rstrip("\n")


def test_ralph_runs_body_while_condition_is_true():
    source = """slop count = 3✨
ralph count > 0 {
    hallucinate(count)✨
    count = count - 1✨
}
hallucinate(“liftoff”)✨"""
    assert run(source) == "3\n2\n1\nliftoff\n"


def test_ralph_exits_when_condition_becomes_false():
    source = """slop i = 0✨
ralph i < 4 {
    i = i + 1✨
}
hallucinate(i)✨"""
    assert run(source) == "4\n"


def test_ralph_skips_body_when_condition_is_false_initially():
    source = """slop ran = ❌✨
ralph ❌ {
    ran = ✅✨
    hallucinate(“body”)✨
}
hallucinate(ran)✨"""
    assert run(source) == "❌\n"


def test_ralph_checks_condition_before_first_iteration():
    source = """slop checks = 0✨
clanker keep_going() {
    checks = checks + 1✨
    ship checks < 2✨
}
ralph keep_going() {
    hallucinate(“body”, checks)✨
}
hallucinate(“checks”, checks)✨"""
    assert run(source) == "body 1\nchecks 2\n"


def test_ralph_allows_the_same_local_declaration_each_iteration():
    source = """slop i = 0✨
ralph i < 3 {
    slop doubled = i * 2✨
    hallucinate(doubled)✨
    i = i + 1✨
}"""
    assert run(source) == "0\n2\n4\n"


def test_ralph_body_locals_do_not_leak_after_the_loop():
    source = """slop i = 0✨
ralph i < 1 {
    slop inside = 42✨
    i = i + 1✨
}
hallucinate(inside)✨"""
    assert fails(source) == "SlopLang runtime error at line 6: undefined variable 'inside'"


def test_nested_ralph_loops_run_independently():
    source = """slop row = 0✨
ralph row < 2 {
    slop column = 0✨
    ralph column < 2 {
        hallucinate(row, column)✨
        column = column + 1✨
    }
    row = row + 1✨
}"""
    assert run(source) == "0 0\n0 1\n1 0\n1 1\n"


def test_ship_exits_a_ralph_loop_inside_a_clanker():
    source = """clanker first_multiple_of_three(n) {
    slop i = 1✨
    ralph i <= n {
        vibe i * 3 >= n {
            ship i * 3✨
        }
        i = i + 1✨
    }
    ship 0✨
}
hallucinate(first_multiple_of_three(7))✨"""
    assert run(source) == "9\n"


def test_zero_iteration_loop_does_not_execute_ship():
    source = """clanker choose() {
    ralph ❌ {
        ship “loop”✨
    }
    ship “after”✨
}
hallucinate(choose())✨"""
    assert run(source) == "after\n"


def test_ralph_condition_must_be_a_boolean():
    assert fails("ralph 0 { }") == (
        "SlopLang runtime error at line 1: ralph condition must be a boolean, got number"
    )


def test_ralph_checks_the_condition_type_before_running_the_body():
    result = run_source("""ralph 0 {
    hallucinate(“body”)✨
}""")
    assert result.stdout == ""
    assert result.stderr == (
        "SlopLang runtime error at line 1: ralph condition must be a boolean, got number\n"
    )


def test_runtime_error_inside_ralph_body_reports_the_body_line():
    source = """slop i = 0✨
ralph i < 1 {
    hallucinate(missing)✨
}"""
    assert fails(source) == "SlopLang runtime error at line 3: undefined variable 'missing'"


@pytest.mark.parametrize(
    ("condition", "expected"),
    [
        ("✅ && ✅", "0\n"),
        ("✅ || ❌", "0\n"),
        ("1 < 2", "0\n"),
        ("!(1 == 2)", "0\n"),
    ],
)
def test_ralph_conditions_accept_boolean_expressions(condition: str, expected: str):
    # Every body decrements once, so a true condition runs the body exactly once.
    source = f"""slop i = 1✨
ralph ({condition}) && i > 0 {{
    i = i - 1✨
}}
hallucinate(i)✨"""
    assert run(source) == expected
