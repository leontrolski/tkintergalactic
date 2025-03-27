from __future__ import annotations

import os
import sys
import tkinter as tk
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Concatenate, Generic, Literal, ParamSpec, overload

from tkintergalactic import diff, events, widgets

P = ParamSpec("P")

Font = widgets.Font
Frame = widgets.Frame
Button = widgets.Button
Entry = widgets.Entry
Text = widgets.Text
EventKeyRelease = events.EventKeyRelease
EventButtonRelease = events.EventButtonRelease1


@dataclass(kw_only=True)
class Window:
    title: str = ""
    w: int | None = None
    h: int | None = None
    app: Callable[[], widgets.Widget]
    previous: widgets.Widget | None = None
    debug: bool = False
    _tk: tk.Tk = None  # type: ignore

    def run(self) -> None:
        try:
            self._tk = tk.Tk()
        except tk.TclError:
            # If TCL is not in the virtualenv (eg. when installed via uv), try the root python lib
            os.environ["TCL_LIBRARY"] = str(Path(sys.base_prefix) / "lib" / "tcl8.6")
            os.environ["TK_LIBRARY"] = str(Path(sys.base_prefix) / "lib" / "tk8.6")
            self._tk = tk.Tk()

        self._tk.title(self.title)
        if self.w is not None and self.h is not None:
            self._tk.geometry(f"{self.w}x{self.h}")
        self.render()
        # Hack to get Mac to focus the window, you still might need to wiggle it
        self._tk.after(1, lambda: self.call("focus", "-force", ".0"))
        self._tk.mainloop()

    def call(self, *args: str | tuple[str, ...]) -> Any:
        if self.debug:
            print(args)
        return self._tk.call(args)

    def render(self) -> None:
        if self.debug:
            print("Render loop")

        this = self.app()
        name(this)

        python_commands_previous = diff.all_commands(self.previous)
        python_commands_this = diff.all_commands(this)
        for python_command, t_event in python_commands_this - python_commands_previous:
            self._tk.createcommand(python_command.name, _Wrapped(self, python_command, t_event))  # type: ignore[no-untyped-call]
        for python_command, t_event in python_commands_previous - python_commands_this:
            self._tk.deletecommand(python_command.name)

        by_both: dict[str, dict[str, list[str | tuple[str, ...]]]] = defaultdict(lambda: defaultdict(list))
        for widget_name, arg in diff.diff_args(self.previous, this):
            by_both[widget_name][arg.command].extend(arg.flags)
            if arg.and_ is not None:
                by_both[widget_name][arg.and_.command].extend(arg.and_.flags)

        for widget_name, by_command in by_both.items():
            for command, is_subcommand in widgets.COMMAND_PRECEDENCE.items():
                if (flags := by_command.get(command)) is not None:
                    if is_subcommand:
                        self.call(widget_name, command, *flags)
                    else:
                        self.call(command, widget_name, *flags)

        self.previous = this
        self.call("update")


# Helpers


@dataclass
class _Wrapped(Generic[events.TEvent]):
    window: Window
    command: widgets.Command[events.TEvent, []]
    t_event: type[events.TEvent]

    def __call__(self, *args: str) -> None:
        if isinstance(self.command, widgets.CommandE):
            event = self.t_event.from_args(args)
            if isinstance(event, events.EventKeyRelease):
                event.value = self.window.call(event.name, "get")
            self.command.f(event, *self.command.args, **self.command.kwargs)
        else:
            self.command.f(*self.command.args, **self.command.kwargs)
        self.window.render()


# Recursively mutates widget to add .name
def name(widget: widgets.Widget, prefix: str = "", i: int = 0) -> None:
    widget.name = f"{prefix}.{i}"
    if isinstance(widget, widgets.Frame):
        for j, child in enumerate(widget.children, start=1):
            name(child, widget.name, i + j)


@overload
def command(
    with_event: Literal[False] = False,
) -> Callable[[Callable[P, None]], widgets.Command[events.TEvent, P]]: ...
@overload
def command(
    with_event: Literal[True],
) -> Callable[[Callable[Concatenate[events.TEvent, P], None]], widgets.CommandE[events.TEvent, P]]: ...
def command(  # type: ignore[misc]
    with_event: bool = False,
) -> Callable[[Callable[Concatenate[events.TEvent, P], None] | Callable[P, None]], widgets.Command[events.TEvent, P]]:
    def inner(
        f: Callable[Concatenate[events.TEvent, P], None] | Callable[P, None],
    ) -> widgets.Command[events.TEvent, P]:
        name = f"{f.__module__}.{f.__name__}"
        return (widgets.CommandE if with_event else widgets.Command)(
            f=f,  # type: ignore[arg-type]
            name=name,
        )

    return inner
