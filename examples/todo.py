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
