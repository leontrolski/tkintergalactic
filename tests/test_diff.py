import tkintergalactic as tk
from tkintergalactic import diff, widgets


def test_no_diff() -> None:
    a = tk.Entry(
        value="a",
    )
    b = tk.Entry(
        value="a",
    )
    tk.name(a)
    tk.name(b)
    actual = sorted(diff.diff_args(a, b), key=lambda p: repr(p))
    expected = list[tuple[str, widgets.Arg]]()
    assert actual == expected


DELETE = widgets.Arg(
    command="delete",
    flags=("0", "end"),
)


def test_diff_from_scratch() -> None:
    a = None
    b = tk.Entry(
        value="b",
    )
    tk.name(b)
    actual = sorted(diff.diff_args(a, b), key=lambda p: repr(p))
    expected = [
        (".0", widgets.Arg(command="configure", flags=("-font", ("Courier", "18")))),
        (".0", widgets.Arg(command="configure", flags=("-state", "normal"))),
        (".0", widgets.Arg(command="entry", flags=())),
        (".0", widgets.Arg(command="insert", flags=("end", "b"), and_=DELETE)),
        (".0", widgets.Arg(command="pack", flags=("-expand", "0"))),
        (".0", widgets.Arg(command="pack", flags=("-fill", "none"))),
        (".0", widgets.Arg(command="pack", flags=("-side", "top"))),
        (".0", widgets.Arg(command="pack", flags=())),
    ]
    assert actual == expected


def test_simple_diff() -> None:
    a = tk.Entry(
        value="a",
    )
    b = tk.Entry(
        value="b",
    )
    tk.name(a)
    tk.name(b)
    actual = sorted(diff.diff_args(a, b), key=lambda p: repr(p))
    expected = [
        (".0", widgets.Arg(command="insert", flags=("end", "b"), and_=DELETE)),
    ]
    assert actual == expected


def test_nested_diff_add() -> None:
    a = tk.Frame(
        tk.Entry(
            value="a",
        ),
        tk.Entry(
            value="b",
        ),
        side="top",
    )
    b = tk.Frame(
        tk.Entry(
            value="a",
        ),
        tk.Entry(
            value="x",
        ),
        tk.Entry(
            value="y",
        ),
        side="bottom",
    )
    tk.name(a)
    tk.name(b)
    actual = sorted(diff.diff_args(a, b), key=lambda p: repr(p))
    expected = [
        (".0", widgets.Arg(command="pack", flags=("-side", "bottom"))),
        (".0.2", widgets.Arg(command="insert", flags=("end", "x"), and_=DELETE)),
        (".0.3", widgets.Arg(command="configure", flags=("-font", ("Courier", "18")))),
        (".0.3", widgets.Arg(command="configure", flags=("-state", "normal"))),
        (".0.3", widgets.Arg(command="entry", flags=())),
        (".0.3", widgets.Arg(command="insert", flags=("end", "y"), and_=DELETE)),
        (".0.3", widgets.Arg(command="pack", flags=("-expand", "0"))),
        (".0.3", widgets.Arg(command="pack", flags=("-fill", "none"))),
        (".0.3", widgets.Arg(command="pack", flags=("-side", "top"))),
        (".0.3", widgets.Arg(command="pack", flags=())),
    ]
    assert actual == expected


def test_nested_diff_remove() -> None:
    a = tk.Frame(
        tk.Entry(
            value="a",
        ),
        tk.Entry(
            value="b",
        ),
        side="top",
    )
    b = tk.Frame(
        tk.Entry(
            value="",
        ),
        side="bottom",
    )
    tk.name(a)
    tk.name(b)
    actual = sorted(diff.diff_args(a, b), key=lambda p: repr(p))
    expected = [
        (".0", widgets.Arg(command="pack", flags=("-side", "bottom"))),
        (".0.1", widgets.Arg(command="insert", flags=("end", ""), and_=DELETE)),
        (".0.2", widgets.Arg(command="destroy", flags=())),
    ]
    assert actual == expected
