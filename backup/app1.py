import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import math

class SiteLayoutApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Site Layout for Sensors")
        self.master.geometry("800x600")

        self.canvas = tk.Canvas(master, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.boundary_points = []
        self.sensor_image = None
        self.sensor_tk = None
        self.sensor_angle = 0  # Angle in degrees
        self.sensor_position = (0, 0)  # Position of the sensor on the canvas

        # Buttons
        self.load_sensor_button = tk.Button(master, text="Load Sensor", command=self.load_sensor)
        self.load_sensor_button.pack(side=tk.LEFT)

        self.add_boundary_button = tk.Button(master, text="Add Boundary", command=self.add_boundary)
        self.add_boundary_button.pack(side=tk.LEFT)

        self.set_sensor_properties_button = tk.Button(master, text="Set Sensor Properties", command=self.set_sensor_properties)
        self.set_sensor_properties_button.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Left click for placing points
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)  # Dragging to move sensor

    def load_sensor(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if file_path:
            self.sensor_image = Image.open(file_path).convert("RGBA")
            self.sensor_tk = ImageTk.PhotoImage(self.sensor_image)
            self.sensor_position = (100, 100)  # Default position for the sensor
            self.canvas.create_image(self.sensor_position, image=self.sensor_tk, anchor=tk.CENTER, tags="sensor")

    def add_boundary(self):
        # This will allow the user to define the boundary
        length = simpledialog.askfloat("Input Length", "Enter the length of the boundary in meters:")
        if length is not None:
            self.boundary_points.append(length)
            print(f"Added boundary length: {length} meters")  # You can store or display this length

    def set_sensor_properties(self):
        detection_range = simpledialog.askfloat("Sensor Detection Range", "Enter the detection range in meters:")
        detection_angle = simpledialog.askfloat("Sensor Detection Angle", "Enter the detection angle in degrees:")
        if detection_range is not None and detection_angle is not None:
            print(f"Sensor Detection Range: {detection_range} meters, Angle: {detection_angle} degrees")

    def on_canvas_click(self, event):
        # Place the sensor at the clicked location
        if self.sensor_tk:
            self.sensor_position = (event.x, event.y)
            self.canvas.delete("sensor")  # Remove previous sensor
            self.canvas.create_image(self.sensor_position, image=self.sensor_tk, anchor=tk.CENTER, tags="sensor")

    def on_mouse_drag(self, event):
        # Move the sensor with mouse dragging
        if self.sensor_tk:
            self.sensor_position = (event.x, event.y)
            self.canvas.delete("sensor")  # Remove previous sensor
            self.canvas.create_image(self.sensor_position, image=self.sensor_tk, anchor=tk.CENTER, tags="sensor")

if __name__ == "__main__":
    root = tk.Tk()
    app = SiteLayoutApp(root)
    root.mainloop()
