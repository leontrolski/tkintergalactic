import itertools
from typing import Iterator

from tkintergalactic import events, widgets


# Very basic diff algorithm
def diff_args(a: widgets.Widget | None, b: widgets.Widget | None) -> Iterator[tuple[str, widgets.Arg]]:
    if b is None:
        if a is not None:
            yield a.name, widgets.Arg("destroy")
        return

    a_args = set[widgets.Arg]()
    a_children = list[widgets.Widget]()
    if a is not None:
        if a.name != b.name or type(a) is not type(b):
            yield a.name, widgets.Arg("destroy")
        a_args = a.args
        if isinstance(a, widgets.Frame):
            a_children = a.children

    for arg in b.args - a_args:
        yield b.name, arg
    if isinstance(b, widgets.Frame):
        for x, y in itertools.zip_longest(a_children, b.children):
            yield from diff_args(x, y)


def all_commands(a: widgets.Widget | None) -> set[tuple[widgets.CommandEither[events.EventAll], type[events.EventAll]]]:
    if a is None:
        return set()
    child_commands = set[tuple[widgets.CommandEither[events.EventAll], type[events.EventAll]]]()
    if isinstance(a, widgets.Frame):
        for child in a.children:
            child_commands |= all_commands(child)
    return a.commands | child_commands
