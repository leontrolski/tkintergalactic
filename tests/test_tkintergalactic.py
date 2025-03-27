import datetime as dt
from dataclasses import dataclass
from typing import Annotated

import tkintergalactic as tk
from tkintergalactic import events, widgets


def test_events() -> None:
    assert tk.events.EventButtonRelease1.to_substitution_str() == "%T %W %t"
    assert tk.events.EventButtonRelease1.from_args(["3", "W", "1234560000000"]) == tk.events.EventButtonRelease1(
        type_field=3,
        name="W",
        time=dt.datetime(2009, 2, 13, 21, 20),
    )
    assert tk.events.EventKeyRelease.to_substitution_str() == "%T %W %t %k %K %N %A"


@dataclass(kw_only=True)
class _HasDisabled:
    disabled: Annotated[
        bool, widgets.ArgField(bool, "configure", "-state", lambda v: "disabled" if v else "normal")
    ] = False


@dataclass(kw_only=True)
class Foo(widgets._WidgetBase, _HasDisabled): ...


def test_args() -> None:
    bar = tk.Entry(
        value="asdad",
        side="left",
        state="disabled",
        expand=True,
        fill="x",
    )
    assert bar.args == {
        widgets.Arg(command="entry", flags=()),
        widgets.Arg(command="pack", flags=()),
        widgets.Arg(command="pack", flags=("-expand", "1")),
        widgets.Arg(command="pack", flags=("-side", "left")),
        widgets.Arg(command="pack", flags=("-fill", "x")),
        widgets.Arg(
            command="insert",
            flags=("end", "asdad"),
            and_=widgets.Arg(
                command="delete",
                flags=("0", "end"),
            ),
        ),
        widgets.Arg(command="configure", flags=("-font", ("Courier", "18"))),
        widgets.Arg(command="configure", flags=("-state", "disabled")),
    }


@tk.command(with_event=True)
def f(e: tk.EventKeyRelease) -> None: ...


def test_commands() -> None:
    bar = tk.Entry(
        value="asdad",
        onkeyrelease=f,
    )
    assert bar._command_fields() == {"onkeyrelease": events.EventKeyRelease}
    assert bar.commands == {(f, events.EventKeyRelease)}
