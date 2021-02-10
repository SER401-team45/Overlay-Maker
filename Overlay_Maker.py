"""
Script for GUI tool used to generate polygon data used as overlay in videos
Script uses Tkinter fo GUI and saves and loads overlay data in JSON
"""

import tkinter as tk
from PIL import ImageTk, Image
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import Canvas
import os
import json


#  Class for Region data
class Region:
    def __init__(self, name_):
        self.name = name_
        self.point_list = []

    def add_point(self, x, y):
        self.point_list.append((x, y))


#  Instance variables
Regions = {}
Selected = None
image = None
grid_overlay = False


# ------------------- FUNCTIONS ------------------ #


def load_image():
    global image
    tk.Tk().withdraw()
    filename = askopenfilename()
    if filename != "":
        load = Image.open(filename)
        [image_width, image_height] = load.size

        if image_height > image_width:
            load = load.resize((500, int(image_height * 500 / image_width)))
        else:
            load = load.resize((int(image_width * 500 / image_height), 500))

        image = ImageTk.PhotoImage(load)

        canvas.config(width=image.width(), height=image.height())

        render()


def load_overlay():
    global image
    tk.Tk().withdraw()
    filename = askopenfilename()
    if filename != "":
        with open(filename) as json_file:
            Regions.clear()
            deselect_region()
            listbox.select_clear(0, tk.END)
            listbox.delete(0, tk.END)

            data = json.load(json_file)
            for reg_json in data["data"]:
                reg = Region(reg_json["name"])
                for point_json in reg_json["points"]:
                    reg.add_point(float(point_json["x"]), float(point_json["y"]))
                Regions[reg.name] = reg
                listbox.insert(0, reg.name)

    render()


def save_overlay():
    data = {"data": []}

    for name in Regions:
        reg = Regions[name]
        reg_data = {"name": name,
                    "points": []}
        for point in reg.point_list:
            reg_data["points"].append({"x": point[0],
                                       "y": point[1]})
        data["data"].append(reg_data)

    with open(asksaveasfilename(defaultextension=".json"), 'w') as outfile:
        json.dump(data, outfile)


def toggle_grid_overlay():
    global grid_overlay
    grid_overlay = not grid_overlay
    render()


def add_dialog():
    answer = tk.simpledialog.askstring("Input", "Name of Action Region?",
                                       parent=window)
    if answer == "":
        tk.messagebox.showinfo("Invalid", "Invalid Entry", parent=window)
        add_dialog()
    elif answer is not None:
        if answer in listbox.get(0, "end"):
            tk.messagebox.showinfo("Invalid", "Region names must be unique", parent=window)
            add_dialog()
        else:
            add_region(answer)


def add_region(name):
    global Selected
    listbox.insert(0, name)
    listbox.select_clear(0, tk.END)
    listbox.select_set(0)
    Selected = name
    Regions[name] = Region(name)


def delete_dialog():
    global Selected
    if Selected is not None:
        answer = tk.messagebox.askokcancel("Question", "Are you sure you want to delete " + str(Selected) + "?")
        if answer:
            delete_region()


def delete_region():
    global Selected
    idx = listbox.get(0, tk.END).index(Selected)
    listbox.delete(idx)
    Regions.pop(Selected)
    Selected = None
    render()


def delete_point():
    if Selected is not None:
        points = Regions[Selected].point_list
        if len(points) > 0:
            points.pop()
            render()


def add_point(x, y):
    global image
    canvas.create_oval(x, y, x+7, y+7, outline="#1f1", fill="#1f1", width=2)
    Regions[Selected].add_point(x/image.width(), y/image.height())
    render()


def render():
    global image, grid_overlay
    if image is not None:
        width = image.width()
        height = image.height()
        canvas.delete("all")
        canvas.create_image(2, 2, anchor=tk.NW, image=image)
        canvas.pack(fill=tk.BOTH, expand=1)

        if grid_overlay:
            num_lines = 20
            for i in range(num_lines):
                canvas.create_line(i*(width/num_lines), 0, i*(width/num_lines), height, width=1)
                canvas.create_line(0, i*(height/num_lines), width, i*(height/num_lines), width=1)

        for name in Regions:
            region = Regions[name]

            if len(region.point_list) > 0:
                point_init = region.point_list[0]
                x_init = point_init[0] * width
                y_init = point_init[1] * height

                color = "#1f1"
                if Selected == name:
                    color = "#f11"

                text_pos_x = 0
                text_pos_y = 0

                coords = []
                x, y = 0, 0
                for point in region.point_list:
                    x = point[0] * width
                    y = point[1] * height
                    text_pos_x += x
                    text_pos_y += y
                    coords.append(x)
                    coords.append(y)
                    canvas.create_oval(x - 3, y - 3, x + 3, y + 3, outline="", fill=color, width=2)

                text_pos_x /= len(region.point_list)
                text_pos_y /= len(region.point_list)
                if text_pos_x < len(name)*5:
                    text_pos_x = len(name)*5
                elif text_pos_x > width - len(name)*5:
                    text_pos_x = width - len(name)*5

                if text_pos_y < 10:
                    text_pos_y = 10
                elif text_pos_y > height - 10:
                    text_pos_y = height - 10

                canvas.create_rectangle(text_pos_x - len(name)*5, text_pos_y-8,
                                        text_pos_x+len(name)*5, text_pos_y+12, fill='black')

                canvas.create_polygon(coords, outline=color, fill="", width=3)

                if Selected == name:
                    canvas.create_oval(x_init - 6, y_init - 6, x_init + 6, y_init + 6,
                                       outline=color, fill="black", width=2)
                    canvas.create_oval(x - 6, y - 6, x + 6, y + 6, outline=color, fill="yellow", width=2)

                canvas.create_text(text_pos_x, text_pos_y, fill="white", font="Calibri 15 bold", text=name)


def deselect_region():
    global Selected
    Selected = None
    listbox.select_clear(0, tk.END)
    render()


# ------------------- GUI ------------------ #


window = tk.Tk(screenName="test")
window.title("Overlay Maker")

menu = tk.Menu(window)
window.config(menu=menu)

fileMenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="Load Image", command=load_image)
fileMenu.add_command(label="Load Overlay", command=load_overlay)
fileMenu.add_command(label="Save Overlay", command=save_overlay)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=window.quit)

toolMenu = tk.Menu(menu)
menu.add_cascade(label="Tools", menu=toolMenu)
toolMenu.add_checkbutton(label="Grid Overlay", command=toggle_grid_overlay)

shortcutMenu = tk.Menu(menu)
menu.add_cascade(label="Shortcuts", menu=shortcutMenu)
shortcutMenu.add_command(label="Enter ------- new region")
shortcutMenu.add_command(label="Esc --------- deselect region")
shortcutMenu.add_command(label="Delete ------ delete region")
shortcutMenu.add_command(label="Back Space - delete Point")


# ------------------- top FRAME ------------------ #


frame_top = tk.Frame(window, bg="red")
frame_top.pack(padx=20, pady=5)

label_frame_title = tk.Label(frame_top, text="Overlay Maker")
label_frame_title.pack(side=tk.TOP)

h_rule1 = tk.Frame(window, height=1, bg="grey")
h_rule1.pack(fill=tk.X)


# ------------------- BUTTON FRAME ------------------ #


frame_Button = tk.Frame(window, width=100)
frame_Button.pack(side=tk.LEFT, fill=tk.Y, expand=1)

frame_button_grid = tk.Frame(frame_Button)
frame_button_grid.pack(side=tk.TOP)

button_load_image = tk.Button(frame_button_grid, text="Load Image", width=12, command=lambda: load_image())
button_load_image.grid(row=0, column=0, padx=10, pady=10)

button_load_overlay = tk.Button(frame_button_grid, text="Load Overlay", width=12, command=lambda: load_overlay())
button_load_overlay.grid(row=1, column=0, padx=10, pady=10)

button_save_overlay = tk.Button(frame_button_grid, text="Save Overlay", width=12, command=lambda: save_overlay())
button_save_overlay.grid(row=2, column=0, padx=10, pady=10)

button_add_region = tk.Button(frame_button_grid, text="Add Region", width=12, command=lambda: add_dialog())
button_add_region.grid(row=3, column=0, padx=10, pady=10)

listbox = tk.Listbox(frame_button_grid,
                     height=10,
                     width=15,
                     bg="white",
                     activestyle='dotbox')
listbox.grid(row=4, column=0, padx=10, pady=10)

button_delete_point = tk.Button(frame_button_grid, text="Delete Point", width=12, command=lambda: delete_point())
button_delete_point.grid(row=5, column=0, padx=10, pady=10)

button_delete_region = tk.Button(frame_button_grid, text="Delete Region", width=12, command=lambda: delete_dialog())
button_delete_region.grid(row=6, column=0, padx=10, pady=10)


# ------------------- IMAGE FRAME ------------------ #


image_frame = tk.Frame(window)
image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

canvas = tk.Canvas(image_frame, width=500, height=500)
canvas.create_image(2, 2, anchor=tk.NW, image=image)
canvas.pack(fill=tk.BOTH, expand=1)


# ------------------- EVENT HANDLERS ------------------ #


def left_click(event):
    print(event)
    global Selected, image
    x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    y = canvas.winfo_pointery() - canvas.winfo_rooty()
    if (image is not None) and (0 <= x <= image.width()) and (0 <= y <= image.height()):
        if Selected is not None:
            add_point(x, y)
    else:
        sel_idx = listbox.curselection()
        if len(sel_idx) > 0:
            new_selected = listbox.get(sel_idx)
            if new_selected != Selected:
                Selected = new_selected
                render()


def key_press(event):
    print(event.keycode)
    if event.keycode == 46:  # Delete Key
        delete_dialog()
    elif event.keycode == 27:  # Escape Key
        deselect_region()
    elif event.keycode == 13:  # Enter Key
        add_dialog()
    elif event.keycode == 8:  # BackSpace Key
        delete_point()


window.bind("<Button-1>", left_click)
window.bind("<Key>", key_press)

# ------------------- MAINLOOP ------------------ #

window.mainloop()
