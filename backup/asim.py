import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import random
import math

class Sensor:
    def __init__(self, x, y, angle=0, detection_range=0, detection_angle=0, is_enabled=False, name=''):
        self.x = x
        self.y = y
        self.angle = angle
        self.detection_range = detection_range
        self.detection_angle = detection_angle
        self.is_enabled = is_enabled
        self.name = name
        self.triggered = False  # Tracks if the sensor is triggered

class Intruder:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SensorSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Simulation")

        # Create a frame for buttons (toolbar)
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # Canvas settings
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, bg='white')
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Control buttons
        self.add_sensor_button = tk.Button(self.toolbar, text="Add Sensor", command=self.add_sensor)
        self.add_sensor_button.pack(pady=5)

        self.add_intruder_button = tk.Button(self.toolbar, text="Add Intruder", command=self.add_random_intruder)
        self.add_intruder_button.pack(pady=5)

        self.add_drone_button = tk.Button(self.toolbar, text="Add Drone", command=self.add_drone)
        self.add_drone_button.pack(pady=5)

        self.delete_sensor_button = tk.Button(self.toolbar, text="Delete Sensor", command=self.delete_selected_sensor)
        self.delete_sensor_button.pack(pady=5)

        self.delete_intruder_button = tk.Button(self.toolbar, text="Delete Intruder", command=self.delete_intruder)
        self.delete_intruder_button.pack(pady=5)

        self.delete_drone_button = tk.Button(self.toolbar, text="Delete Drone", command=self.delete_drone)
        self.delete_drone_button.pack(pady=5)

        # Create rotation slider
        self.rotation_slider = tk.Scale(self.toolbar, from_=0, to=360, orient=tk.HORIZONTAL, label="Rotate Sensor", command=self.update_sensor_rotation)
        self.rotation_slider.pack(pady=5)

        # Load images
        self.sensor_image_path = "static/images/sensor.png"
        self.sensor_on_image_path = "static/images/sensor_on.png"
        self.sensor_off_image_path = "static/images/sensor_off.png"
        self.intruder_image_path = "static/images/intruder.png"
        self.drone_image_path = "static/images/drone.png"  # Add the path for drone image

        self.sensor_image = self.load_sensor_image(self.sensor_image_path, (25, 25))
        self.sensor_on_image = self.load_sensor_image(self.sensor_on_image_path, (25, 25))
        self.sensor_off_image = self.load_sensor_image(self.sensor_off_image_path, (25, 25))
        self.intruder_image = self.load_sensor_image(self.intruder_image_path, (20, 45))
        self.drone_image = self.load_sensor_image(self.drone_image_path, (30, 30))  # Load drone image

        # Initialize sensor, intruder, and drone lists
        self.sensors = []
        self.selected_sensor = None
        self.dragging_sensor = None
        self.intruder = None  
        self.dragging_intruder = None  
        self.drone = None  # Track the drone
        self.dragging_drone = None  # Track the dragging state of the drone

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<Double-Button-1>", self.open_sensor_config)

        # Draw initial grid
        self.draw_grid()

    def load_sensor_image(self, path, size):
        try:
            image = Image.open(path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Image Load Error", f"Failed to load image: {e}")
            return None

    def draw_grid(self):
        for i in range(0, 1920, 25):  # Vertical lines
            self.canvas.create_line(i, 0, i, 1080, fill="#ddd")
        for i in range(0, 1080, 25):  # Horizontal lines
            self.canvas.create_line(0, i, 1920, i, fill="#ddd")

    def add_sensor(self):
        x = random.randint(0, 750)
        y = random.randint(0, 550)
        new_sensor = Sensor(x, y)
        self.sensors.append(new_sensor)
        self.redraw_canvas()

    def add_random_intruder(self):
        if not self.intruder:  # Only add one intruder
            x = random.randint(0, 750)
            y = random.randint(0, 550)
            self.intruder = Intruder(x, y)
            self.redraw_canvas()

    def add_drone(self):
        if not self.drone:  # Only add one drone
            x = random.randint(0, 750)
            y = random.randint(0, 550)
            self.drone = Drone(x, y)
            self.redraw_canvas()

    def delete_intruder(self):
        self.intruder = None
        self.redraw_canvas()

    def delete_drone(self):
        self.drone = None
        self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.draw_grid()

        for sensor in self.sensors:
            self.draw_sensor(sensor)
            self.draw_field_of_view(sensor)  # Always draw the FOV to check if it's triggered

        if self.intruder:
            self.canvas.create_image(self.intruder.x + 25, self.intruder.y + 45, image=self.intruder_image, anchor=tk.CENTER)

        if self.drone:
            self.canvas.create_image(self.drone.x + 15, self.drone.y + 15, image=self.drone_image, anchor=tk.CENTER)  # Centering drone image

        # Check for alarm after redrawing
        self.check_alarm()

    def draw_sensor(self, sensor):
        image_to_draw = self.sensor_on_image if sensor.is_enabled else self.sensor_off_image
        x = sensor.x + 12.5
        y = sensor.y + 12.5
        self.canvas.create_image(x, y, image=image_to_draw, anchor=tk.CENTER)
        self.canvas.create_text(x, y - 25, text=sensor.name, fill="black", font=("Arial", 10))

    def draw_field_of_view(self, sensor):
        if not sensor.is_enabled:
            return
        
        detection_range_pixels = sensor.detection_range * 25  # Change to 25 for 1 meter
        angle_rad = math.radians(sensor.angle)

        # Calculate start and end angles based on detection_angle
        start_angle = angle_rad - math.radians(sensor.detection_angle / 2)
        end_angle = angle_rad + math.radians(sensor.detection_angle / 2)

        # Sensor position (bottom center)
        sensor_center_x = sensor.x + 12.5
        sensor_center_y = sensor.y + 25  # Change to 25 for the bottom of the sensor image

        # Create points for the arc
        points = []
        num_points = 100  # Number of points to define the arc
        for i in range(num_points + 1):
            t = i / num_points  # Normalize t to [0, 1]
            theta = start_angle + t * (sensor.detection_angle * math.pi / 180)  # Convert to radians
            x = sensor_center_x + detection_range_pixels * math.cos(theta)
            y = sensor_center_y + detection_range_pixels * math.sin(theta)
            points.extend((x, y))
        
        # Create the arc outline and fill
        color = 'red' if sensor.triggered else 'lightgreen'
        self.canvas.create_polygon(points, fill=color, outline='')

    def check_alarm(self):
        for sensor in self.sensors:
            if sensor.is_enabled:
                detection_range_pixels = sensor.detection_range * 25  # Change to 25 for 1 meter
                sensor_center_x = sensor.x + 12.5
                sensor_center_y = sensor.y + 25  # Bottom of the sensor image

                # Calculate distance to the intruder
                if self.intruder:
                    distance_to_intruder = math.sqrt((self.intruder.x + 25 - sensor_center_x) ** 2 + (self.intruder.y + 45 - sensor_center_y) ** 2)

                    if distance_to_intruder <= detection_range_pixels and self.is_within_angle(sensor, self.intruder):
                        sensor.triggered = True
                    else:
                        sensor.triggered = False

                # Update the triggered state of the sensor based on detection
                sensor.triggered = self.intruder and distance_to_intruder <= detection_range_pixels and self.is_within_angle(sensor, self.intruder)

    def is_within_angle(self, sensor, intruder):
        angle_rad = math.radians(sensor.angle)
        intruder_angle = math.atan2(intruder.y + 45 - (sensor.y + 25), intruder.x + 25 - (sensor.x + 12.5))
        angle_difference = abs(angle_rad - intruder_angle)
        
        # Normalize the angle difference to be within 180 degrees
        angle_difference = min(angle_difference, 2 * math.pi - angle_difference)

        return angle_difference <= math.radians(sensor.detection_angle / 2)

    def on_canvas_click(self, event):
        # Check if clicking on a sensor
        for sensor in self.sensors:
            if sensor.x <= event.x <= sensor.x + 25 and sensor.y <= event.y <= sensor.y + 25:
                self.selected_sensor = sensor
                self.dragging_sensor = sensor
                # Set the rotation slider to the sensor's current angle
                self.rotation_slider.set(sensor.angle)
                break
        else:
            # Check if clicking on the intruder
            if self.intruder and self.intruder.x <= event.x <= self.intruder.x + 50 and self.intruder.y <= event.y <= self.intruder.y + 90:
                self.dragging_intruder = self.intruder
            # Check if clicking on the drone
            elif self.drone and self.drone.x <= event.x <= self.drone.x + 30 and self.drone.y <= event.y <= self.drone.y + 30:
                self.dragging_drone = self.drone
            else:
                self.selected_sensor = None
                self.rotation_slider.set(0)  # Reset slider if no sensor is selected

    def on_mouse_drag(self, event):
        if self.dragging_sensor:
            self.dragging_sensor.x = event.x - 12.5
            self.dragging_sensor.y = event.y - 12.5
            self.redraw_canvas()
        elif self.dragging_intruder:
            self.dragging_intruder.x = event.x - 25
            self.dragging_intruder.y = event.y - 45
            self.redraw_canvas()
        elif self.dragging_drone:
            self.dragging_drone.x = event.x - 15
            self.dragging_drone.y = event.y - 15
            self.redraw_canvas()

    def on_mouse_release(self, event):
        self.dragging_sensor = None
        self.dragging_intruder = None
        self.dragging_drone = None  # Reset drone dragging

    def open_sensor_config(self, event):
        if not self.selected_sensor:
            return

        sensor = self.selected_sensor
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Sensor")

        tk.Label(dialog, text="Sensor Name:").pack()
        name_entry = tk.Entry(dialog)
        name_entry.pack()
        name_entry.insert(0, sensor.name)

        tk.Label(dialog, text="Detection Range (meters):").pack()
        range_entry = tk.Entry(dialog)
        range_entry.pack()
        range_entry.insert(0, sensor.detection_range)

        tk.Label(dialog, text="Detection Angle (degrees):").pack()
        angle_entry = tk.Entry(dialog)
        angle_entry.pack()
        angle_entry.insert(0, sensor.detection_angle)

        enabled_var = tk.BooleanVar(value=sensor.is_enabled)
        tk.Checkbutton(dialog, text="Enable Sensor", variable=enabled_var).pack()

        def save_config():
            sensor.name = name_entry.get()
            sensor.detection_range = float(range_entry.get())
            sensor.detection_angle = float(angle_entry.get())
            sensor.is_enabled = enabled_var.get()
            dialog.destroy()
            self.redraw_canvas()

        tk.Button(dialog, text="Save", command=save_config).pack()

    def delete_selected_sensor(self):
        if self.selected_sensor:
            self.sensors.remove(self.selected_sensor)
            self.selected_sensor = None
            self.redraw_canvas()
        else:
            messagebox.showinfo("No Selection", "Please select a sensor to delete.")




    def update_sensor_rotation(self, angle):
        if self.selected_sensor:
            # Update the selected sensor's angle and redraw the canvas
            self.selected_sensor.angle = float(angle)
            self.redraw_canvas()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorSimulationApp(root)
    root.mainloop()
