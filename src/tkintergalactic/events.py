import datetime as dt
import enum
from dataclasses import dataclass
from functools import cache
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Iterable,
    Literal,
    Self,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)


# https://www.tcl-lang.org/man/tcl/TkCmd/bind.html#M7
class EventType(enum.Enum):
    Activate = "Activate"
    ButtonPress = "ButtonPress"
    ButtonRelease = "ButtonRelease"
    Circulate = "Circulate"
    CirculateRequest = "CirculateRequest"
    Colormap = "Colormap"
    Configure = "Configure"
    ConfigureRequest = "ConfigureRequest"
    Create = "Create"
    Deactivate = "Deactivate"
    Destroy = "Destroy"
    Enter = "Enter"
    Expose = "Expose"
    FocusIn = "FocusIn"
    FocusOut = "FocusOut"
    Gravity = "Gravity"
    KeyPress = "KeyPress"
    KeyRelease = "KeyRelease"
    Leave = "Leave"
    Map = "Map"
    MapRequest = "MapRequest"
    Motion = "Motion"
    MouseWheel = "MouseWheel"
    Property = "Property"
    Reparent = "Reparent"
    ResizeRequest = "ResizeRequest"
    TouchpadScroll = "TouchpadScroll"
    Unmap = "Unmap"
    Visibility = "Visibility"
    # https://www.tcl-lang.org/man/tcl/TkCmd/bind.html#M6
    # Handy modified
    ButtonRelease1 = "ButtonRelease-1"


@dataclass
class Substitution:
    s: str
    eg: Any
    doc: str
    converter: Callable[[str], Any] | None = None


@dataclass
class _EventBase:
    @classmethod
    @cache
    def substitutions(cls) -> tuple[Substitution, ...]:
        subs = tuple[Substitution, ...]()
        for t in get_type_hints(cls, include_extras=True).values():
            args = get_args(t)
            if get_origin(t) is not Annotated:
                continue
            sub = next(arg for arg in args if isinstance(arg, Substitution))
            subs += (sub,)
        return subs

    @classmethod
    def to_substitution_str(cls) -> str:
        return " ".join(sub.s for sub in cls.substitutions())

    @classmethod
    def from_args(cls, args: Iterable[str]) -> Self:
        return cls(
            *(  # type: ignore[arg-type]
                arg if sub.converter is None else sub.converter(arg)
                for arg, sub in zip(args, cls.substitutions(), strict=True)
            )
        )

    type_field: Annotated[
        int,
        Substitution(
            "%T",
            3,
            "The type field from the event",
            lambda s: int(s),
        ),
    ]
    name: Annotated[
        str,
        Substitution(
            "%W",
            ".x.y",
            "The path name of the window to which the event was reported (the window field from the event)",
        ),
    ]
    time: Annotated[
        dt.datetime,
        Substitution(
            "%t",
            dt.datetime(2021, 1, 1),
            "The time field from the event. This is the X server timestamp, when the event occurred.",
            lambda s: dt.datetime.fromtimestamp(int(s) / 1000),
        ),
    ]


@dataclass
class EventKeyRelease(_EventBase):
    event_type: ClassVar[Literal[EventType.KeyRelease]] = EventType.KeyRelease

    keycode: Annotated[
        int,
        Substitution(
            "%k",
            16777331,
            "The keycode field from the event.",
            lambda s: int(s),
        ),
    ]
    keysym: Annotated[
        str,
        Substitution(
            "%K",
            "Meta_L",
            "The keysym corresponding to the event, substituted as a textual string.",
        ),
    ]
    keysym_int: Annotated[
        int,
        Substitution(
            "%N",
            65511,
            "The keysym corresponding to the event, substituted as a decimal number.",
            lambda s: int(s),
        ),
    ]
    unicode_char: Annotated[
        str | None,
        Substitution(
            "%A",
            "",
            "Substitutes the UNICODE character corresponding to the event, or the empty string if the event does not correspond to a UNICODE character (e.g. the shift key was pressed). On X11, XmbLookupString (or XLookupString when input method support is turned off) does all the work of translating from the event to a UNICODE character. On X11, valid only for Key event. On Windows and macOS/aqua, valid only for Key and KeyRelease events.",
            lambda s: s if s else None,
        ),
    ]

    # Special attribute - this is fetched _after_ we receive the event
    value: str = ""


@dataclass
class EventButtonRelease1(_EventBase):
    event_type: ClassVar[Literal[EventType.ButtonRelease1]] = EventType.ButtonRelease1


EventAll = EventKeyRelease | EventButtonRelease1

TEvent = TypeVar("TEvent", bound=EventAll)

"""
Notes from https://www.tcl-lang.org/man/tcl/TkCmd/bind.html#M26

Valid for all event types.
    %T  The type field from the event.
    %W  The path name of the window to which the event was reported (the window field from the event).
    %t  The time field from the event. This is the X server timestamp (typically the time since the last server reset) in milliseconds, when the event occurred.

Valid only for KeyRelease events.
    %k  The keycode field from the event.
    %K  The keysym corresponding to the event, substituted as a textual string.
    %N  The keysym corresponding to the event, substituted as a decimal number.
    %A  Substitutes the UNICODE character corresponding to the event, or the empty string if the event does not correspond to a UNICODE character (e.g. the shift key was pressed). On X11, XmbLookupString (or XLookupString when input method support is turned off) does all the work of translating from the event to a UNICODE character. On X11, valid only for Key event. On Windows and macOS/aqua, valid only for Key and KeyRelease events.

TODO: implement these
Valid for Button, ButtonRelease, Motion, Key, KeyRelease, and MouseWheel events.
    %b  The number of the button that was pressed or released.
    %x, %y  The x and y fields from the event. , %x and %y indicate the position of the mouse pointer relative to the receiving window. For key events on the Macintosh these are the coordinates of the mouse at the moment when an X11 KeyEvent is sent to Tk, which could be slightly later than the time of the physical press or release. For Enter and Leave events, the position where the mouse pointer crossed the window, relative to the receiving window. For Configure and Create requests, the x and y coordinates of the window relative to its parent window.
Valid only for Enter and Leave events.
    %f  The focus field from the event (0 or 1). 1 if the receiving window is the focus window or a descendant of the focus window, 0 otherwise.
Valid for the Configure, ConfigureRequest, Create, ResizeRequest, and Expose events.
    %h  The height field from the event. Indicates the new or requested height of the window.
    %w  The width field from the event. Indicates the new or requested width of the window.
Valid for all event types.
    %#  The number of the last client request processed by the server (the serial field from the event).
    %i  The window field from the event, represented as a hexadecimal integer.
    %E  The send_event field from the event. 0 indicates that this is a “normal” event, 1 indicates that it is a “synthetic” event generated by SendEvent.
    %M  The number of script-based binding patterns matched so far for the event.
Valid only for Configure events. Indicates the sibling window immediately below the receiving window in the stacking order, or 0 if the receiving window is at the bottom.
    %a  The above field from the event, formatted as a hexadecimal number.
Valid only for Expose events. Indicates that there are count pending Expose events which have not yet been delivered to the window.
    %c  The count field from the event.
    %d  The detail or user_data field from the event. The %d is replaced by a string identifying the detail.
        For Enter, Leave, FocusIn, and FocusOut events, the string will be one of the following: NotifyAncestor, NotifyNonlinearVirtual, NotifyDetailNone, NotifyPointer, NotifyInferior, NotifyPointerRoot, NotifyNonlinear, NotifyVirtual
        For ConfigureRequest events, the string will be one of: Above, Opposite, Below, None, BottomIf, TopIf
        For virtual events, the string will be whatever value is stored in the user_data field when the event was created (typically with event generate), or the empty string if the field is NULL. Virtual events corresponding to key sequence presses (see event add for details) set the user_data to NULL. For events other than these, the substituted string is undefined.
Valid only for Enter, FocusIn, FocusOut, and Leave events.
    %m  The mode field from the event. The substituted string is one of NotifyNormal, NotifyGrab, NotifyUngrab, or NotifyWhileGrabbed.
Valid only for Map, Reparent, and Configure events.
    %o  The override_redirect field from the event.
Valid only for Circulate and CirculateRequest events.
    %p  The place field from the event, substituted as one of the strings PlaceOnTop or PlaceOnBottom.
Valid for Button, ButtonRelease, Enter, Key, KeyRelease, Leave, and Motion events, a decimal string is substituted. For Visibility, one of the strings VisibilityUnobscured, VisibilityPartiallyObscured, and VisibilityFullyObscured is substituted. For Property events, substituted with either the string NewValue (indicating that the property has been created or modified) or Delete (indicating that the property has been removed).
    %s  The state field from the event.
Valid only for Configure, ConfigureRequest, and Create events.
    %B  The border_width field from the event.
    %D  This reports the delta value of a MouseWheel event. The delta value represents the rotation units the mouse wheel has been moved. The sign of the value represents the direction the mouse wheel was scrolled.
Valid only for Property events.
    %P  The name of the property being updated or deleted (which may be converted to an XAtom using winfo atom.)
Valid only for events containing a root field.
    %R  The root window identifier from the event.
Valid only for events containing a subwindow field.
    %S  The subwindow window identifier from the event, formatted as a hexadecimal number.
Valid only for Button, ButtonRelease, Enter, Key, KeyRelease, Leave and Motion events. Same meaning as %x and %y, except relative to the (virtual) root window.
    %X, %Y  The x_root and y_root fields from the event. If a virtual-root window manager is being used then the substituted values are the corresponding x-coordinate and y-coordinate in the virtual root.
"""
