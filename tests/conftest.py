import io
import subprocess
from typing import Any

import ocdiff
import ocdiff.helpers
import rich.console


def rich_repr(o: Any) -> str:
    string_io = io.StringIO()
    rich.console.Console(
        file=string_io,
        width=ocdiff.helpers.terminal_width() // 2 - 10,
        tab_size=4,
        no_color=True,
        highlight=False,
        log_time=False,
        log_path=False,
    ).print(o)
    string_io.seek(0)
    return string_io.getvalue()


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--copy-left",
        action="store_true",
        help="Copy the rich_repr of the LHS to the clipboard",
    )


def pytest_assertrepr_compare(config: Any, op: str, left: Any, right: Any) -> list[str] | None:
    very_verbose = config.option.verbose >= 2
    if not very_verbose:
        return None

    if op != "==":
        return None

    try:
        if abs(left + right) < 100:
            return None
    except TypeError:
        pass

    if config.getoption("--copy-left"):
        subprocess.run("pbcopy", text=True, input=rich_repr(left))

    try:
        if isinstance(left, str) and isinstance(right, str):
            pretty_left = left
            pretty_right = right
        else:
            pretty_left = rich_repr(left)
            pretty_right = rich_repr(right)
        return ocdiff.console_diff(
            pretty_left,
            pretty_right,
            context_lines=10,
            max_total_width=ocdiff.helpers.terminal_width() - len("E     "),
        ).splitlines()
    except Exception:
        return None
