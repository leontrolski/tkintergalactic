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
