import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class BlueprintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blueprint Tracing Application")

        # Toolbar
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # Load Blueprint button
        self.load_button = tk.Button(self.toolbar, text="Load Blueprint", command=self.load_blueprint)
        self.load_button.pack(pady=5)

        # Save button
        self.save_button = tk.Button(self.toolbar, text="Save Image", command=self.save_image)
        self.save_button.pack(pady=5)

        # Clear canvas button
        self.clear_button = tk.Button(self.toolbar, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(pady=5)

        # Canvas settings
        self.canvas = tk.Canvas(root, width=1980, height=1080, bg='white')
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Variables to manage blueprint position and size
        self.blueprint_position = (0, 0)  # Position of the blueprint on the canvas
        self.blueprint_size = (1980, 1080)  # Size of the blueprint
        self.dragging = False  # Dragging flag
        self.resizing = False  # Resizing flag
        self.prev_x = 0
        self.prev_y = 0
        self.corner_offset = 10  # Size of the corner for resizing
        self.selected_corner = None  # Which corner is being resized
        self.grid_spacing = 50  # 1 meter = 50 pixels

        # Mouse bindings
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def load_blueprint(self):
        file_path = filedialog.askopenfilename(title="Select Blueprint Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.current_image = Image.open(file_path)
            self.blueprint_size = (self.current_image.width, self.current_image.height)
            self.display_blueprint()

    def display_blueprint(self):
        self.blueprint_image = ImageTk.PhotoImage(self.current_image.resize(self.blueprint_size, Image.LANCZOS))
        self.canvas.create_image(self.blueprint_position[0], self.blueprint_position[1], image=self.blueprint_image, anchor=tk.NW)

        # Draw resize corners
        self.draw_resize_corners()
        # Draw grid with updated spacing
        self.draw_grid()

    def draw_resize_corners(self):
        # Clear previous corners
        self.canvas.delete("resize_corner")
        
        # Define corner positions
        x, y = self.blueprint_position
        width, height = self.blueprint_size

        # Draw corners
        corners = [
            (x, y),  # Top-left
            (x + width, y),  # Top-right
            (x, y + height),  # Bottom-left
            (x + width, y + height)  # Bottom-right
        ]

        for corner in corners:
            self.canvas.create_rectangle(corner[0] - self.corner_offset, corner[1] - self.corner_offset,
                                          corner[0] + self.corner_offset, corner[1] + self.corner_offset,
                                          fill="red", outline="red", tags="resize_corner")

    def draw_grid(self):
        # Draw a grid every 50 pixels (1 meter)
        for x in range(0, 1980, self.grid_spacing):
            self.canvas.create_line(x, 0, x, 1080, fill='lightgray', dash=(2, 2))  # Vertical lines
        for y in range(0, 1080, self.grid_spacing):
            self.canvas.create_line(0, y, 1980, y, fill='lightgray', dash=(2, 2))  # Horizontal lines

        # Draw scale indicator in the top-left corner
        scale_text = f"1 Block = 1 Meter"
        self.canvas.create_text(20, 20, text=scale_text, anchor=tk.NW, fill='black', font=('Arial', 12, 'bold'))

    def on_button_press(self, event):
        if self.is_resizing_corner(event.x, event.y):
            self.resizing = True
            self.selected_corner = self.get_resizing_corner(event.x, event.y)
        else:
            self.prev_x = event.x
            self.prev_y = event.y
            self.dragging = True

    def is_resizing_corner(self, x, y):
        # Check if the click is near any corner
        for corner in self.get_corners():
            if (corner[0] - self.corner_offset <= x <= corner[0] + self.corner_offset and
                    corner[1] - self.corner_offset <= y <= corner[1] + self.corner_offset):
                return True
        return False

    def get_resizing_corner(self, x, y):
        # Identify which corner is being resized
        corners = self.get_corners()
        for i, corner in enumerate(corners):
            if (corner[0] - self.corner_offset <= x <= corner[0] + self.corner_offset and
                    corner[1] - self.corner_offset <= y <= corner[1] + self.corner_offset):
                return i
        return None

    def get_corners(self):
        # Calculate the current corners based on position and size
        x, y = self.blueprint_position
        width, height = self.blueprint_size
        return [
            (x, y),  # Top-left
            (x + width, y),  # Top-right
            (x, y + height),  # Bottom-left
            (x + width, y + height)  # Bottom-right
        ]

    def on_mouse_drag(self, event):
        if self.dragging:
            # Update the position of the blueprint
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            self.blueprint_position = (self.blueprint_position[0] + dx, self.blueprint_position[1] + dy)
            self.redraw_blueprint()
            self.prev_x = event.x
            self.prev_y = event.y
        elif self.resizing:
            self.resize_blueprint(event.x, event.y)

    def resize_blueprint(self, x, y):
        # Get the size of the blueprint before resizing
        original_width, original_height = self.blueprint_size
        # Resize based on which corner is being dragged
        if self.selected_corner == 0:  # Top-left corner
            new_width = max(original_width - (x - self.blueprint_position[0]), 50)  # Minimum width
            new_height = max(original_height - (y - self.blueprint_position[1]), 50)  # Minimum height
            self.blueprint_position = (self.blueprint_position[0] + (original_width - new_width), self.blueprint_position[1] + (original_height - new_height))
        elif self.selected_corner == 1:  # Top-right corner
            new_width = max(x - self.blueprint_position[0], 50)  # Minimum width
            new_height = max(original_height - (y - self.blueprint_position[1]), 50)  # Minimum height
        elif self.selected_corner == 2:  # Bottom-left corner
            new_width = max(original_width - (x - self.blueprint_position[0]), 50)  # Minimum width
            new_height = max(y - self.blueprint_position[1], 50)  # Minimum height
            self.blueprint_position = (self.blueprint_position[0] + (original_width - new_width), self.blueprint_position[1])
        elif self.selected_corner == 3:  # Bottom-right corner
            new_width = max(x - self.blueprint_position[0], 50)  # Minimum width
            new_height = max(y - self.blueprint_position[1], 50)  # Minimum height

        self.blueprint_size = (new_width, new_height)
        self.redraw_blueprint()

    def on_button_release(self, event):
        self.dragging = False
        self.resizing = False

    def redraw_blueprint(self):
        # Clear canvas and redraw the blueprint
        self.canvas.delete("all")
        self.display_blueprint()

    def save_image(self):
        if self.current_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                self.current_image.save(save_path)
                messagebox.showinfo("Save Image", "Image saved successfully!")

    def clear_canvas(self):
        self.canvas.delete("all")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BlueprintApp(root)
    root.mainloop()
