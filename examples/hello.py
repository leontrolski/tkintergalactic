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
