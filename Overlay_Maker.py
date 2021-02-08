import tkinter as tk
from PIL import ImageTk, Image
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import Canvas
import os
import json


class Region:
    def __init__(self, name_):
        self.name = name_
        self.point_list = []

    def add_point(self, x, y):
        self.point_list.append((x, y))


Regions = {}
Selected = None
image = None


# ------------------- FUNCTIONS ------------------ #
def LoadImage():
    global image
    tk.Tk().withdraw()
    filename = askopenfilename()
    if filename != "":
        load = Image.open(filename)
        [imageWidth, imageHeight] = load.size

        if imageHeight > imageWidth:
            load = load.resize((500, int(imageHeight * 500 / imageWidth)))
        else:
            load = load.resize((int(imageWidth * 500 / imageHeight), 500))

        image = ImageTk.PhotoImage(load)

        canvas.config(width=image.width(), height=image.height())

        Render()


def LoadOverlay():
    tk.Tk().withdraw()
    filename = askopenfilename()
    if filename != "":
        with open(filename) as json_file:
            Regions.clear()
            DeselectRegion()
            listbox.select_clear(0, tk.END)
            listbox.delete(0, tk.END)

            data = json.load(json_file)
            for reg_json in data["data"]:
                reg = Region(reg_json["name"])
                for point_json in reg_json["points"]:
                    reg.add_point(float(point_json["x"]), float(point_json["y"]))
                Regions[reg.name] = reg
                listbox.insert(0, reg.name)
    Render()


def SaveOverlay():
    data = {}
    data["data"] = []

    for name in Regions:
        reg = Regions[name]
        reg_data = {}
        reg_data["name"] = name
        reg_data["points"] = []
        for point in reg.point_list:
            reg_data["points"].append({"x": point[0],
                                       "y": point[1]})
        data["data"].append(reg_data)

    with open(asksaveasfilename(defaultextension=".json"), 'w') as outfile:
        json.dump(data, outfile)


def AddDialog():
    answer = tk.simpledialog.askstring("Input", "Name of Action Region?",
                                       parent=window)
    if answer == "":
        tk.messagebox.showinfo("Invalid", "Invalid Entry", parent=window)
        AddDialog()
    elif answer is not None:
        if answer in listbox.get(0, "end"):
            tk.messagebox.showinfo("Invalid", "Region names must be unique", parent=window)
            AddDialog()
        else:
            AddRegion(answer)


def AddRegion(name):
    global Selected
    listbox.insert(0, name)
    listbox.select_clear(0, tk.END)
    listbox.select_set(0)
    Selected = name
    Regions[name] = Region(name)


def DeleteDialog():
    global Selected
    if Selected is not None:
        answer = tk.messagebox.askokcancel("Question", "Are you sure you want to delete " + Selected + "?")
        if answer:
            DeleteRegion()


def DeleteRegion():
    global Selected
    idx = listbox.get(0, tk.END).index(Selected)
    listbox.delete(idx)
    Regions.pop(Selected)
    Selected = None
    Render()


def DeletePoint():
    if Selected is not None:
        points = Regions[Selected].point_list
        if len(points) > 0:
            points.pop()
            Render()


def AddPoint(x, y):
    global image
    canvas.create_oval(x, y, x+7, y+7, outline="#1f1", fill="#1f1", width=2)
    Regions[Selected].add_point(x/image.width(), y/image.height())
    Render()


def Render():
    global image
    width = image.width()
    height = image.height()
    canvas.delete("all")
    canvas.create_image(2, 2, anchor=tk.NW, image=image)
    canvas.pack(fill=tk.BOTH, expand=1)

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
                canvas.create_oval(x_init - 6, y_init - 6, x_init + 6, y_init + 6, outline=color, fill="black", width=2)
                canvas.create_oval(x - 6, y - 6, x + 6, y + 6, outline=color, fill="yellow", width=2)

            canvas.create_text(text_pos_x, text_pos_y, fill="white", font="Calibri 15 bold", text=name)


def DeselectRegion():
    global Selected
    Selected = None
    listbox.select_clear(0, tk.END)
    Render()

# ------------------- GUI ------------------ #

window = tk.Tk(screenName="test")
window.title("Model Interface")

menu = tk.Menu(window)
window.config(menu=menu)

subMenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Load Image", command=LoadImage)
subMenu.add_command(label="Load Overlay", command=LoadOverlay)
subMenu.add_command(label="Save Overlay", command=SaveOverlay)
subMenu.add_separator()
subMenu.add_command(label="Exit", command=window.quit)

# ------------------- TOP FRAME ------------------ #

frame_Top = tk.Frame(window, bg="red")
frame_Top.pack(padx=20, pady=5)

label_FrameTitle = tk.Label(frame_Top, text="Overlay Maker")
label_FrameTitle.pack(side=tk.TOP)

h_rule1 = tk.Frame(window, height=1, bg="grey")
h_rule1.pack(fill=tk.X)

# ------------------- BUTTON FRAME ------------------ #

frame_Button = tk.Frame(window, width=100)
frame_Button.pack(side=tk.LEFT, fill=tk.Y, expand=1)

frame_ButtonGrid = tk.Frame(frame_Button)
frame_ButtonGrid.pack(side=tk.TOP)

button_LoadImage = tk.Button(frame_ButtonGrid, text="Load Image", width=12, command=lambda: LoadImage())
button_LoadImage.grid(row=0, column=0, padx=10, pady=10)

button_LoadOverlay = tk.Button(frame_ButtonGrid, text="Load Overlay", width=12, command=lambda: LoadOverlay())
button_LoadOverlay.grid(row=1, column=0, padx=10, pady=10)

button_SaveOverlay = tk.Button(frame_ButtonGrid, text="Save Overlay", width=12, command=lambda: SaveOverlay())
button_SaveOverlay.grid(row=2, column=0, padx=10, pady=10)

button_AddRegion = tk.Button(frame_ButtonGrid, text="Add Region", width=12, command=lambda: AddDialog())
button_AddRegion.grid(row=3, column=0, padx=10, pady=10)

listbox = tk.Listbox(frame_ButtonGrid,
                     height=10,
                     width=15,
                     bg="white",
                     activestyle='dotbox')
listbox.grid(row=4, column=0, padx=10, pady=10)

button_DeletePoint = tk.Button(frame_ButtonGrid, text="Delete Point", width=12, command=lambda: DeletePoint())
button_DeletePoint.grid(row=5, column=0, padx=10, pady=10)

button_DeleteRegion = tk.Button(frame_ButtonGrid, text="Delete Region", width=12, command=lambda: DeleteDialog())
button_DeleteRegion.grid(row=6, column=0, padx=10, pady=10)


# ------------------- IMAGE FRAME ------------------ #

image_frame = tk.Frame(window)
image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

'''load_ = Image.open("test_img.png")
[imageWidth_, imageHeight_] = load_.size
load_ = load_.resize((int(imageWidth_*500/imageHeight_), 500))

image = ImageTk.PhotoImage(load_)'''

canvas = tk.Canvas(image_frame, width=500, height=500)
canvas.create_image(2, 2, anchor=tk.NW, image=image)
canvas.pack(fill=tk.BOTH, expand=1)


def leftclick(event):
    global Selected, image
    x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    y = canvas.winfo_pointery() - canvas.winfo_rooty()
    if 0 <= x <= image.width() and 0 <= y <= image.height():
        if Selected is not None:
            AddPoint(x, y)
    else:
        sel_idx = listbox.curselection()
        if len(sel_idx) > 0:
            new_selected = listbox.get(sel_idx)
            if new_selected != Selected:
                Selected = new_selected
                Render()


def KeyPress(event):
    print(event.keycode)
    if event.keycode == 46:  # Delete Key
        DeleteDialog()
    elif event.keycode == 27:  # Escape Key
        DeselectRegion()
    elif event.keycode == 13:  # Enter Key
        AddDialog()
    elif event.keycode == 8:  # BackSpace Key
        DeletePoint()


window.bind("<Button-1>", leftclick)
window.bind("<Key>", KeyPress)

# ------------------- MAINLOOP ------------------ #

window.mainloop()