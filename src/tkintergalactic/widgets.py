from __future__ import annotations

from dataclasses import dataclass, field, fields
from functools import cache
from types import UnionType
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Concatenate,
    Generic,
    Iterable,
    Iterator,
    Literal,
    ParamSpec,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from tkintergalactic import events

T = TypeVar("T")
P = ParamSpec("P")


@dataclass
class ArgField(Generic[T]):
    t: type[T]
    command: str  # eg: "configure"
    name: str  # eg: "-state"
    to_arg_value: Callable[[T], str | tuple[str, ...]]
    and_: Arg | None = None


@dataclass(frozen=True)
class Arg:
    command: str  # eg: "configure"
    flags: tuple[str | tuple[str, ...], ...] = ()
    and_: Arg | None = None


@dataclass
class Command(Generic[events.TEvent, P]):
    f: Callable[P, None]
    name: str

    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.name)

    def partial(self, *args: P.args, **kwargs: P.kwargs) -> Command[events.TEvent, []]:
        out = Command[events.TEvent, []](
            f=self.f,
            name=self.name,
            args=args,
            kwargs=kwargs,
        )
        # TODO: try some clever stuff with hashable types
        suffix = str(id(out))
        out.name += "_" + suffix
        return out

    def call(self, *args: P.args, **kwargs: P.kwargs) -> None:
        return self.f(*self.args, *args, **self.kwargs, **kwargs)


@dataclass
class CommandE(Command[events.TEvent, P]):
    f: Callable[Concatenate[events.TEvent, P], None]

    def __hash__(self) -> int:
        return hash(self.name)

    def partial(self, *args: P.args, **kwargs: P.kwargs) -> CommandE[events.TEvent, []]:
        return super().partial(*args, **kwargs)  # type: ignore[return-value]


type CommandEither[T: events.EventAll] = Command[T, []] | CommandE[T, []]


COMMAND_PRECEDENCE: dict[str, bool] = {
    "destroy": False,
    # Widget names
    "frame": False,
    "button": False,
    "entry": False,
    "text": False,
    # Other commands
    "delete": True,
    "insert": True,
    "configure": True,
    "pack": False,
    "bind": False,
}

Side = Literal["left", "right", "top", "bottom"]
Fill = Literal["x", "y", "both", "none"]
Relief = Literal["sunken"]
State = Literal["disabled", "normal"]


@dataclass(frozen=True)
class Font:
    family: Literal["Helvetica", "Times", "Courier"] = "Courier"
    size: int = 18
    styles: list[Literal["bold", "roman", "italic", "underline", "overstrike"]] = field(default_factory=list)


ArgFont = Annotated[Font, ArgField(Font, "configure", "-font", lambda v: (v.family, str(v.size), *v.styles))]
ArgState = Annotated[State, ArgField(State, "configure", "-state", lambda v: v)]
ArgHeight = Annotated[int, ArgField(int, "configure", "-height", lambda v: str(v))]
ArgText = Annotated[str, ArgField(str, "configure", "-text", lambda v: v)]
ArgRelief = Annotated[Relief, ArgField(Relief, "configure", "-relief", lambda v: v)]
ArgBorderwidth = Annotated[int, ArgField(int, "configure", "-borderwidth", lambda v: str(v))]
ArgInsertEnd = Annotated[str, ArgField(str, "insert", "end", lambda v: v, and_=Arg("delete", ("0", "end")))]
ArgInsertLineEnd = Annotated[str, ArgField(str, "insert", "end", lambda v: v, and_=Arg("delete", ("1.0", "end")))]
ArgFill = Annotated[Fill, ArgField(Fill, "pack", "-fill", lambda v: v)]
ArgSide = Annotated[Side, ArgField(Side, "pack", "-side", lambda v: v)]
ArgExpand = Annotated[bool, ArgField(bool, "pack", "-expand", lambda v: "1" if v else "0")]


@dataclass
class _WidgetBase:
    @classmethod
    @cache
    def _arg_fields(cls) -> dict[str, ArgField[Any]]:
        out = dict[str, ArgField[Any]]()
        for name, t in get_type_hints(cls, include_extras=True).items():
            args = get_args(t)
            if get_origin(t) is not Annotated:
                continue
            out[name] = next(arg for arg in args if isinstance(arg, ArgField))
        return out

    @classmethod
    @cache
    def _command_fields(cls) -> dict[str, type[events.EventAll]]:
        out = dict[str, type[events.EventAll]]()
        for name, t in get_type_hints(cls).items():
            if get_origin(t) is UnionType:
                for t_inner in get_args(t):
                    if t_inner is not type(None):
                        t = t_inner
            if get_origin(t) is CommandEither:
                [t_event] = get_args(t)
                assert issubclass(t_event, events.EventAll)
                out[name] = t_event
        return out

    widget_name: ClassVar[str]
    name: str = ""
    side: ArgSide = "top"
    fill: ArgFill = "none"
    expand: ArgExpand = False

    args: set[Arg] = field(default_factory=set)
    commands: set[tuple[CommandEither[events.EventAll], type[events.EventAll]]] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.args = {Arg(self.widget_name), Arg("pack")}
        for name, f in self._arg_fields().items():
            v = getattr(self, name)
            assert v is not None
            self.args |= {Arg(f.command, (f.name, f.to_arg_value(v)), f.and_)}

        self.commands = set()
        for name, t_event in self._command_fields().items():
            v = getattr(self, name)
            if v is None:
                continue
            assert isinstance(v, Command)
            if v is None:
                continue
            self.commands.add((v, t_event))
            self.args.add(Arg("bind", (f"<{t_event.event_type.value}>", v.name + " " + t_event.to_substitution_str())))

    def __rich_repr__(self) -> Iterator[tuple[str, Any]]:
        for f in fields(self):
            if f.name in {"args", "commands"}:
                continue
            yield f.name, getattr(self, f.name)


class Frame(_WidgetBase):
    widget_name: ClassVar[Literal["frame"]] = "frame"
    children: list[Widget]
    relief: ArgRelief
    borderwidth: ArgBorderwidth

    def __init__(
        self,
        *children: Widget | Iterable[Widget] | None,
        # TODO: remove these and use ParamSpec or something
        side: ArgSide = "top",
        fill: ArgFill = "none",
        expand: ArgExpand = False,
        relief: ArgRelief = "sunken",
        borderwidth: ArgBorderwidth = 1,
    ) -> None:
        flattened = list[Widget]()
        for child in children:
            if child is None:
                continue
            elif isinstance(child, Iterable):
                flattened.extend(child)
            else:
                flattened.append(child)
        self.children = flattened

        self.side = side
        self.fill = fill
        self.expand = expand
        self.relief = relief
        self.borderwidth = borderwidth
        self.__post_init__()

    def __rich_repr__(self) -> Iterator[tuple[str, Any]]:
        yield "children", self.children


@dataclass(kw_only=True)
class Button(_WidgetBase):
    widget_name: ClassVar[Literal["button"]] = "button"
    text: ArgText
    onbuttonrelease: CommandEither[events.EventButtonRelease1] | None = None
    font: ArgFont = Font()


@dataclass(kw_only=True)
class Entry(_WidgetBase):
    widget_name: ClassVar[Literal["entry"]] = "entry"
    value: ArgInsertEnd
    onkeyrelease: CommandEither[events.EventKeyRelease] | None = None
    font: ArgFont = Font()
    # TODO: allow changing value of "disabled"
    state: ArgState = "normal"


@dataclass(kw_only=True)
class Text(_WidgetBase):
    widget_name: ClassVar[Literal["text"]] = "text"
    content: ArgInsertLineEnd
    height: ArgHeight = 0  # seemingly in rem
    font: ArgFont = Font()
    # TODO: allow changing content of "disabled"
    state: ArgState = "normal"

    def __post_init__(self) -> None:
        if self.height == 0:
            self.height = len(self.content.splitlines())
        super().__post_init__()


Widget = Frame | Button | Entry | Text
