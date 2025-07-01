import tkinter as tk

root = tk.Tk()
root.geometry("250x200")
frame = tk.Frame(root, height=180)
frame.pack(fill="x", expand=False)
frame.pack_propagate(False)

canvas = tk.Canvas(frame, height=180)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

container = tk.Frame(canvas)
window_id = canvas.create_window((0, 0), window=container, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
container.bind("<Configure>", on_frame_configure)

def on_canvas_configure(event):
    canvas.itemconfig(window_id, width=event.width)
canvas.bind("<Configure>", on_canvas_configure)

for i in range(30):
    tk.Checkbutton(container, text=f"Checkbox {i+1}").pack(fill="x", padx=4, pady=2)

def scroll_down():
    canvas.yview_scroll(1, "units")
tk.Button(root, text="Scroll Down", command=scroll_down).pack()

root.mainloop()