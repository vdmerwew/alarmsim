import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk

class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Blueprint Tracing Application")
        self.master.geometry("800x600")

        self.canvas = tk.Canvas(master, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.background_image = None
        self.bg_image_tk = None
        self.bg_image_position = (0, 0)
        self.bg_image_size = (800, 600)  # Track the size of the background image
        self.opacity = 204  # Opacity level (0-255, 80% opacity)
        self.walls = []  # List to store wall points
        self.line_lengths = []  # Store lengths for display
        self.temp_line = None  # Temporary line for dragging
        self.straight_line_mode = False  # Flag for straight line mode

        # Buttons
        self.load_background_button = tk.Button(master, text="Load Background", command=self.load_background)
        self.load_background_button.pack(side=tk.LEFT)

        self.undo_button = tk.Button(master, text="Undo", command=self.undo_action)
        self.undo_button.pack(side=tk.LEFT)

        self.calculate_volume_button = tk.Button(master, text="Calculate Volume", command=self.calculate_volume)
        self.calculate_volume_button.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Left click for placing points
        self.master.bind("<Shift_L>", self.enable_straight_line)  # Bind Shift key
        self.master.bind("<KeyRelease-Shift_L>", self.disable_straight_line)  # Unbind Shift key

    def load_background(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.background_image = Image.open(file_path).convert("RGBA")
            self.redraw_background()

    def redraw_background(self):
        self.canvas.delete("background")
        if self.background_image:
            # Create a new image with opacity
            alpha_channel = self.background_image.split()[3].point(lambda p: p * (self.opacity / 255.0))
            background_with_opacity = Image.new("RGBA", self.background_image.size)
            background_with_opacity.paste(self.background_image, (0, 0), alpha_channel)
            self.bg_image_tk = ImageTk.PhotoImage(background_with_opacity.resize(self.bg_image_size, Image.LANCZOS))
            self.canvas.create_image(self.bg_image_position[0], self.bg_image_position[1], image=self.bg_image_tk, anchor=tk.NW, tags="background")

    def on_canvas_click(self, event):
        # Check if it's the first point
        if len(self.walls) == 0:
            self.walls.append((event.x, event.y))  # Add first point
        else:
            last_point = self.walls[-1]
            self.walls.append((event.x, event.y))  # Add new point
            self.canvas.create_line(last_point[0], last_point[1], event.x, event.y, fill='blue', width=2)
            self.prompt_for_length(last_point, (event.x, event.y))

    def prompt_for_length(self, start, end):
        length = simpledialog.askfloat("Input Length", "Enter the length in meters:")
        if length is not None:
            self.line_lengths.append(length)
            self.display_length(length, start, end)

    def display_length(self, length, start, end):
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        self.canvas.create_text(mid_x, mid_y - 10, text=f"{length} m", fill='red')

def undo_action(self):
    if len(self.walls) > 1:
        # Remove the last line and point
        self.walls.pop()  # Remove the last point
        last_length = self.line_lengths.pop()  # Remove the last length

        # Find the last line ID and delete it
        line_id = self.canvas.find_withtag("last_line")
        if line_id:
            self.canvas.delete(line_id)

        # Recalculate lines without affecting the lengths already added
        for i in range(len(self.walls) - 1):
            p1 = self.walls[i]
            p2 = self.walls[i + 1]
            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='blue', width=2, tags="last_line")
    else:
        self.walls.clear()


    def calculate_volume(self):
        total_volume = sum(self.line_lengths)  # Here you can adjust based on your calculation needs
        messagebox.showinfo("Total Volume", f"Total volume calculated: {total_volume} m")

    def enable_straight_line(self, event):
        self.straight_line_mode = True

    def disable_straight_line(self, event):
        self.straight_line_mode = False

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
