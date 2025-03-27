# Tkintergalactic

Declarative Tcl/Tk UI library for Python.
- Somewhat React-like (there is effectively a Tk VDOM).
- Well typed.
- Maps very closely to the underlying Tcl/Tk for ease of debugging.
- Zero dependency.
- On mac sometimes you have to start by wiggling the window.
- Small enough to understand how it works.
- In an incomplete state - much functionality missing.

# Hello World

After `pip install tkintergalactic`, just run:

```python
import tkintergalactic as tk

counter = 0

@tk.command()
def inc_counter() -> None:
    global counter
    counter += 1

tk.Window(
    app=lambda: tk.Frame(
        tk.Button(text="Hello World!", onbuttonrelease=inc_counter),
        tk.Text(content=f"Button clicked {counter} times"),
    ),
).run()
```

![Hello world screencast](examples/screenshots/hello.gif)


# TODO list

```python
from dataclasses import dataclass, field
import tkintergalactic as tk

@dataclass
class Task:
    description: str
    complete: bool = False

@dataclass
class State:
    tasks: list[Task] = field(default_factory=list)
    new_task_description: str = ""

state = State()

@tk.command()
def add_task() -> None:
    state.tasks.append(Task(state.new_task_description))
    state.new_task_description = ""

@tk.command()
def delete_task(i: int) -> None:
    state.tasks.pop(i)

@tk.command()
def toggle_class_complete(i: int) -> None:
    state.tasks[i].complete = not state.tasks[i].complete

@tk.command(with_event=True)
def set_new_task_description(e: tk.EventKeyRelease) -> None:
    state.new_task_description = e.value

tk.Window(
    title="TODO List",
    h=600,
    w=500,
    app=lambda: tk.Frame(
        tk.Frame(
            [
                tk.Frame(
                    tk.Entry(
                        value=task.description,
                        side="left",
                        font=tk.Font(styles=["overstrike"]) if task.complete else tk.Font(),
                        expand=True,
                    ),
                    tk.Button(
                        text="✗" if task.complete else "✔",
                        onbuttonrelease=toggle_class_complete.partial(i=i),
                    ),
                    tk.Button(text="Delete", onbuttonrelease=delete_task.partial(i=i), side="right"),
                    fill="x",
                    expand=True,
                )
                for i, task in enumerate(state.tasks)
            ],
            fill="x",
            expand=True,
        ),
        tk.Frame(
            tk.Entry(
                value=state.new_task_description,
                onkeyrelease=set_new_task_description,
                side="left",
                expand=True,
            ),
            tk.Button(
                text="New Task",
                onbuttonrelease=add_task,
            ),
            fill="x",
        ),
        tk.Text(
            content=f"Total number of tasks: {len(state.tasks)}\nComplete: {sum(t.complete for t in state.tasks)}",
        ),
    ),
).run()
```

![TODO list screencast](examples/screenshots/todo.gif)

# Packer example

The packer is the main way of arranging Widgets.

```python
import tkintergalactic as tk

tk.Window(
    title="Packer",
    w=200,
    h=300,
    app=lambda: tk.Frame(
        tk.Button(text="t", side="top", fill="x"),
        tk.Button(text="b", side="bottom", fill="x"),
        tk.Button(text="l", side="left"),
        tk.Button(text="r", side="right"),
        tk.Text(content="mid", expand=True, fill="both"),
        fill="both",
        expand=True,
    ),
).run()
```

![Packer screenshot](examples/screenshots/packer.png)

# Further work

## Functionality

The majority of the functionality in the [Tk Docs](https://www.tcl-lang.org/man/tcl8.6/TkCmd/contents.htm) is still not implemented, most of it is just a case of padding out existing functionality in `widgets.py`, however there are some complicated text buffer bits that would take a lot more work.

## Diffing

- The diffing algorithm could be made more efficient - see eg. the referenced alogrithms in the `mithril` code.
- Could allow passing optional `id`s to widgets to make diffing long lists more efficient.
- More complicated state management a la React could be done. I'd have a preference for a simpler "this widget tree is the same as the other, don't diff" approach that the user can opt in to.
- Potentially a lot of the diffing code coudld be offloaded to Rust.
- Before doing any of the above, set up benchmarking.

## Other

- Sort out distinct naming for custom python commands, TCL commands and subcommands.

# Development

```
uv pip install -e '.[dev]'
mypy .
pytest -vv
```
