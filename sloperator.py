import sys
from pathlib import Path

from sloperator.errors import SlopError
from sloperator.lexer import tokenize
from sloperator.parser import parse
from sloperator.runner import run_program


def validate_source(source: str) -> SlopError | None:
    try:
        tokens = tokenize(source)
        parse(tokens)
    except SlopError as error:
        return error
    return None


def main(argv: list[str]) -> int:
    check = False
    path_arg = None
    for arg in argv[1:]:
        if arg == "--check":
            check = True
        elif path_arg is None:
            path_arg = arg

    if path_arg is None:
        print("usage: uv run sloperator.py [--check] <file.slop>", file=sys.stderr)
        return 2

    path = Path(path_arg)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"could not read '{path}': {error.strerror}", file=sys.stderr)
        return 2

    if check:
        error = validate_source(source)
        if error is not None:
            print(error, file=sys.stderr)
            return 1
        else:
            print("Syntax OK")
            return 0
    else:
        error = run_program(source, sys.stdout)
        if error is not None:
            sys.stdout.flush()
            print(error, file=sys.stderr)
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
