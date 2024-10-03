import tkinter as tk
from tkinter import filedialog, messagebox,Toplevel, Button, Label
from PIL import Image, ImageTk
import random
import math


class Sensor:
    def __init__(self, x, y, angle=0, detection_range=0, detection_angle=0, is_enabled=False, name=''):
        self.x = x
        self.y = y
        self.angle = angle
        self.detection_range = self.convert_meters_to_pixels(detection_range)
        self.detection_angle = detection_angle
        self.is_enabled = is_enabled
        self.name = name
        self.triggered = False  # Tracks if the sensor is triggered
        

    def convert_meters_to_pixels(self, meters):
        return meters * 50  # 1 meter = 50 pixels

    def set_detection_range(self, range_in_meters):
        self.detection_range = self.convert_meters_to_pixels(range_in_meters)

class Panel:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Intruder:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Drone:
    def __init__(self, x=0, y=0):
        self.gps_points = []
        self.current_location = (x, y)  # Set the initial location of the drone
        self.scanning = False

        
class SensorSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Simulation")

        self.dragging_sensor = None
        self.dragging_intruder = None
        self.dragging_drone = None
        self.dragging_panel = None

        
        
        # Create a frame for buttons (toolbar)
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # Canvas settings
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, bg='white')
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
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

        # Sensor button
        self.add_sensor_button = tk.Button(self.toolbar, text="Add Sensor", command=self.add_sensor)
        self.add_sensor_button.pack(pady=5)
        
        self.add_intruder_button = tk.Button(self.toolbar, text="Add Intruder", command=self.add_random_intruder)
        self.add_intruder_button.pack(pady=5)

        self.add_drone_button = tk.Button(self.toolbar, text="Add Drone", command=self.add_drone)
        self.add_drone_button.pack(pady=5)
        
        self.add_panel_button = tk.Button(self.toolbar, text="Add Panel", command=self.add_panel)
        self.add_panel_button.pack(pady=5)
        self.config_panel_button = tk.Button(self.toolbar, text="Config Panel", command=self.open_panel_config)
        self.config_panel_button.pack(pady=5)

        
        # Load Blueprint button
        self.load_button = tk.Button(self.toolbar, text="Load Blueprint", command=self.load_blueprint)
        self.load_button.pack(pady=5)
        self.delete_blueprint_button = tk.Button(self.toolbar, text="Delete Blueprint", command=self.delete_blueprint)
        self.delete_blueprint_button.pack(pady=5)
        
        self.save_button = tk.Button(self.toolbar, text="Save Blueprint", command=self.save_blueprint)
        self.save_button.pack(pady=5)


        self.current_image = None  # Initialize current_image to None
        
        self.delete_panel_button = tk.Button(self.toolbar, text="Delete Panel", command=self.delete_panel)
        self.delete_panel_button.pack(pady=5)

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
        self.panel_image_path = "static/images/panel.png"  

        self.sensor_image = self.load_sensor_image(self.sensor_image_path, (18, 18))
        self.sensor_on_image = self.load_sensor_image(self.sensor_on_image_path, (18, 18))
        self.sensor_off_image = self.load_sensor_image(self.sensor_off_image_path, (18, 18))
        self.intruder_image = self.load_sensor_image(self.intruder_image_path, (20, 45))
        self.drone_image = self.load_sensor_image(self.drone_image_path, (30, 30))  # Load drone image
        self.panel_image = self.load_sensor_image(self.panel_image_path, (30, 40))  # Load drone image

        # Initialize sensor, intruder,drone and panel
        self.sensors = []
        self.selected_sensor = None
        self.dragging_sensor = None
        self.intruder = None  
        self.dragging_intruder = None  
        self.drone = None  # Track the drone
        self.dragging_drone = None  # Track the dragging state of the drone
        self.panel =None
        self.dragging_panel =None
        self.gps_points = {}

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<Double-Button-1>", self.open_sensor_config)
        

        # Blueprint-related attributes
        self.blueprint_position = (0, 0)
        self.blueprint_size = (1980, 1080)
        self.dragging = False
        self.resizing = False
        self.prev_x = 0
        self.prev_y = 0
        self.corner_offset = 10
        self.selected_corner = None
        self.grid_spacing = 50


        
        # Draw grid
        self.draw_grid()
        
    def check_for_corner_selection(self, x, y):
        corners = [
            (self.blueprint_position[0], self.blueprint_position[1]),  # Top-left
            (self.blueprint_position[0] + self.blueprint_size[0], self.blueprint_position[1]),  # Top-right
            (self.blueprint_position[0], self.blueprint_position[1] + self.blueprint_size[1]),  # Bottom-left
            (self.blueprint_position[0] + self.blueprint_size[0], self.blueprint_position[1] + self.blueprint_size[1])  # Bottom-right
        ]
        
        for i, (cx, cy) in enumerate(corners):
            if abs(cx - x) <= self.corner_offset and abs(cy - y) <= self.corner_offset:
                self.selected_corner = i
                print(f"Selected corner: {self.selected_corner}")  # Debug print
                return True
        
        return False
    
        
    def save_blueprint(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            # Save the current canvas state as an image
            self.canvas.postscript(file=f"{file_path}.eps")
            img = Image.open(f"{file_path}.eps")
            img.save(file_path, 'png')  # Save as PNG

    def on_drag(self, event):
        if self.dragging_blueprint and not self.resizing:
            # Update the position of the blueprint
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            self.blueprint_position = (self.blueprint_position[0] + dx, self.blueprint_position[1] + dy)
            self.redraw_blueprint()
            self.prev_x = event.x
            self.prev_y = event.y
            
    def draw_grid(self):
        # Draw a grid every 50 pixels (1 meter)
        for x in range(0, 1980, self.grid_spacing):
            self.canvas.create_line(x, 0, x, 1080, fill='lightgray', dash=(2, 2))  # Vertical lines
        for y in range(0, 1080, self.grid_spacing):
            self.canvas.create_line(0, y, 1980, y, fill='lightgray', dash=(2, 2))  # Horizontal lines

        # Draw scale indicator in the top-left corner
        scale_text = "1 Block = 1 Meter"
        self.canvas.create_text(20, 20, text=scale_text, anchor=tk.NW, fill='black', font=('Arial', 12, 'bold'))

    def load_blueprint(self):
        file_path = filedialog.askopenfilename(title="Select Blueprint Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.current_image = Image.open(file_path)
            self.blueprint_size = (self.current_image.width, self.current_image.height)
            self.blueprint_position = (0, 0)  # Reset position or set to desired default
            self.display_blueprint()
            
    #alles blueprint related
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

    

    def on_button_press(self, event):
        print(f"Mouse click coordinates: ({event.x}, {event.y})")  # Debug
        self.selected_corner = self.get_resizing_corner(event.x, event.y)  # Try to get the corner first
        if self.selected_corner is not None:  # If a corner is selected
            self.resizing = True
            print(f"Selected corner after detection: {self.selected_corner}")  # Debug
        else:
            self.prev_x = event.x
            self.prev_y = event.y
            self.dragging = True
            print("Not resizing, starting drag...")  # Debug


    def is_resizing_corner(self, x, y):
        for corner in self.get_corners():
            if (corner[0] - self.corner_offset <= x <= corner[0] + self.corner_offset and
                    corner[1] - self.corner_offset <= y <= corner[1] + self.corner_offset):
                print(f"Resizing corner detected at: {corner}")  # Debug
                return True
        print("No resizing corner detected.")  # Debug
        return False



    def get_resizing_corner(self, x, y):
        corners = self.get_corners()
        print(f"Checking corners: {corners}")  # Debug: Show current corners
        for i, corner in enumerate(corners):
            print(f"Checking corner {i}: {corner}")  # Debug
            if (corner[0] - self.corner_offset <= x <= corner[0] + self.corner_offset and
                    corner[1] - self.corner_offset <= y <= corner[1] + self.corner_offset):
                print(f"Resizing corner confirmed: {corner} (Index: {i})")  # Debug
                return i  # Return the index of the selected corner
        print("No valid corner found.")  # Debug
        return None




    def get_corners(self):
        # Calculate the current corners based on position and size
        x, y = self.blueprint_position
        width, height = self.blueprint_size
        corners = [
            (x, y),  # Top-left
            (x + width, y),  # Top-right
            (x, y + height),  # Bottom-left
            (x + width, y + height)  # Bottom-right
        ]
        print(f"Current corners: {corners}")  # Debug: Show calculated corner positions
        return corners


    def resize_blueprint(self, x, y):
        # Ensure that a corner is selected
        if self.selected_corner is None:
            return  # Exit if no corner is selected

        # Get the size and position of the blueprint before resizing
        original_width, original_height = self.blueprint_size

        # Initialize new_width and new_height with current sizes
        new_width = original_width
        new_height = original_height

        # Resize based on which corner is being dragged
        if self.selected_corner == 0:  # Top-left corner
            new_width = max(original_width - (x - self.blueprint_position[0]), 50)  # Minimum width
            new_height = max(original_height - (y - self.blueprint_position[1]), 50)  # Minimum height
            self.blueprint_position = (self.blueprint_position[0] + (original_width - new_width), 
                                    self.blueprint_position[1] + (original_height - new_height))
        elif self.selected_corner == 1:  # Top-right corner
            new_width = max(x - self.blueprint_position[0], 50)  # Minimum width
            new_height = max(original_height - (y - self.blueprint_position[1]), 50)  # Minimum height
        elif self.selected_corner == 2:  # Bottom-left corner
            new_width = max(original_width - (x - self.blueprint_position[0]), 50)  # Minimum width
            new_height = max(y - self.blueprint_position[1], 50)  # Minimum height
            self.blueprint_position = (self.blueprint_position[0] + (original_width - new_width), 
                                    self.blueprint_position[1])
        elif self.selected_corner == 3:  # Bottom-right corner
            new_width = max(x - self.blueprint_position[0], 50)  # Minimum width
            new_height = max(y - self.blueprint_position[1], 50)  # Minimum height

        # Update blueprint size
        self.blueprint_size = (new_width, new_height)
        self.redraw_blueprint()

    def on_button_release(self, event):
        # Reset dragging and resizing states
        self.dragging = False
        self.resizing = False
        self.dragging_sensor = None
        self.dragging_intruder = None
        self.dragging_drone = None
        self.dragging_panel = None

    def redraw_blueprint(self):
        # Clear canvas and redraw the blueprint
        self.canvas.delete("all")
        self.display_blueprint()
    #tot hier bluprint

    def load_sensor_image(self, path, size):
        try:
            image = Image.open(path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Image Load Error", f"Failed to load image: {e}")
            return None

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
            print(f"Drone added at position: {self.drone.current_location}")
            self.redraw_canvas()  # Redraw canvas after adding the drone

            
    def add_panel(self):
        if not self.panel:  # Only add if panel doesn't exist
            self.panel = Panel(random.randint(50, 800), random.randint(50, 800))
            self.canvas.create_image(self.panel.x, self.panel.y, image=self.panel_image, anchor=tk.NW)

    
    def delete_blueprint(self):
        self.current_image = None  # Remove blueprint image
        self.canvas.delete("all")  # Clear everything
        self.redraw_canvas()  # Redraw without the blueprint
        
    def delete_selected_sensor(self):
            if self.selected_sensor:
                self.sensors.remove(self.selected_sensor)
                self.selected_sensor = None
                self.redraw_canvas()
            else:
                messagebox.showinfo("No Selection", "Please select a sensor to delete.")

    def delete_intruder(self):
        self.intruder = None
        self.redraw_canvas()

    def delete_drone(self):
        self.drone = None
        self.redraw_canvas()
    
    def delete_panel(self):
        if self.panel:
            self.canvas.delete("panel")  # Ensure you assign a unique tag to the panel when creating it
            self.panel = None

    def redraw_canvas(self):
        self.canvas.delete("all")  # Clear the canvas
        self.draw_grid()  # Draw the grid

        # Draw the blueprint if it exists
        if hasattr(self, 'current_image') and self.current_image:
            self.redraw_blueprint()

        # Draw sensors and their fields of view
        for sensor in self.sensors:
            self.draw_sensor(sensor)
            self.draw_field_of_view(sensor)

        # Draw intruder if it exists
        if self.intruder:
            self.canvas.create_image(self.intruder.x + 25, self.intruder.y + 45, image=self.intruder_image, anchor=tk.CENTER)

        # Draw drone if it exists
        if self.drone:
            drone_x, drone_y = self.drone.current_location  # Access the current location of the drone
            self.canvas.create_image(drone_x + 15, drone_y + 15, image=self.drone_image, anchor=tk.CENTER)

        # Draw panel if it exists
        if self.panel:
            self.canvas.create_image(self.panel.x + 30, self.panel.y + 40, image=self.panel_image, anchor=tk.CENTER)

        self.check_alarm()  # Check for alarms after redrawing



    def draw_sensor(self, sensor):
        image_to_draw = self.sensor_on_image if sensor.is_enabled else self.sensor_off_image
        x = sensor.x + 12.5
        y = sensor.y + 12.5
        self.canvas.create_image(x, y, image=image_to_draw, anchor=tk.CENTER)
        self.canvas.create_text(x, y - 25, text=sensor.name, fill="black", font=("Arial", 10))

    def is_intruder_detected(self, sensor, intruder):
        # Calculate detection range in pixels
        detection_range_pixels = sensor.detection_range * 50  # Convert meters to pixels
        sensor_x, sensor_y = sensor.x + 12.5, sensor.y + 25  # Center position of the sensor

        # Calculate distance to intruder
        intruder_distance = math.sqrt((intruder.x - sensor_x) ** 2 + (intruder.y - sensor_y) ** 2)

        # Check if intruder is within detection range
        if intruder_distance <= detection_range_pixels:
            # Calculate the angle to the intruder
            angle_to_intruder = math.degrees(math.atan2(intruder.y - sensor_y, intruder.x - sensor_x))

            # Normalize sensor angle to the same range as angle_to_intruder (-180 to 180 degrees)
            normalized_sensor_angle = sensor.angle % 360
            if normalized_sensor_angle > 180:
                normalized_sensor_angle -= 360

            # Calculate the angle difference
            angle_difference = abs(angle_to_intruder - normalized_sensor_angle)

            # Normalize the angle difference to within [0, 180] degrees
            if angle_difference > 180:
                angle_difference = 360 - angle_difference

            # Check if the intruder is within the sensor's detection angle
            if angle_difference <= sensor.detection_angle / 2:
                sensor.triggered = True  # Intruder detected
                return True  # Intruder is detected
        sensor.triggered = False  # No intruder detected
        return False  # Intruder is outside FOV





    def draw_field_of_view(self, sensor):
        if not sensor.is_enabled:
            return

        detection_range_pixels = sensor.detection_range * 50  # 50 pixels per meter
        angle_rad = math.radians(sensor.angle)

        # Calculate start and end angles based on detection_angle
        start_angle = angle_rad - math.radians(sensor.detection_angle / 2)
        end_angle = angle_rad + math.radians(sensor.detection_angle / 2)

        # Sensor position (bottom center)
        sensor_center_x = sensor.x + 12.5
        sensor_center_y = sensor.y + 25  # Bottom of the sensor image

        # Create points for the arc
        points = [sensor_center_x, sensor_center_y]
        num_points = 100  # Number of points to define the arc
        for i in range(num_points + 1):
            t = i / num_points  # Normalize t to [0, 1]
            theta = start_angle + t * (end_angle - start_angle)
            x = sensor_center_x + detection_range_pixels * math.cos(theta)
            y = sensor_center_y + detection_range_pixels * math.sin(theta)
            points.extend((x, y))

        # Set the color based on the trigger status
        color = 'red' if sensor.triggered else 'lightgreen'

        # Draw the FOV polygon
        self.canvas.create_polygon(points, fill=color, outline='', stipple='gray25')  # Adjust stipple as needed



        
      

    def check_alarm(self):
        for sensor in self.sensors:
            if sensor.is_enabled:
                detection_range_pixels = sensor.detection_range * 50  # 50 pixels per meter
                sensor_center_x = sensor.x + 12.5
                sensor_center_y = sensor.y + 25  # Bottom of the sensor image

                # Only check for intruder detection if intruder exists
                if self.intruder:
                    # Calculate the distance to the intruder
                    distance_to_intruder = math.sqrt((self.intruder.x + 25 - sensor_center_x) ** 2 + (self.intruder.y + 45 - sensor_center_y) ** 2)

                    # Check if the distance is within the detection range and within the detection angle
                    if distance_to_intruder <= detection_range_pixels and self.is_within_angle(sensor, self.intruder):
                        sensor.triggered = True  # Intruder detected
                    else:
                        sensor.triggered = False  # No intruder detected
                else:
                    sensor.triggered = False  # No intruder present
            else:
                sensor.triggered = False  # Sensor is not enabled


    def is_within_angle(self, sensor, intruder):
        # Convert sensor's angle to radians
        angle_rad = math.radians(sensor.angle)

        # Calculate the angle to the intruder from the sensor
        dx = intruder.x + 25 - (sensor.x + 12.5)
        dy = intruder.y + 45 - (sensor.y + 25)
        intruder_angle = math.atan2(dy, dx)

        # Normalize the angles to be in the range [0, 2π]
        angle_difference = abs(angle_rad - intruder_angle) % (2 * math.pi)

        # Check if the intruder is within the FOV angle
        half_detection_angle = math.radians(sensor.detection_angle / 2)
        return angle_difference <= half_detection_angle


    def on_drag_drone(self, event):
        if self.dragging and self.drone:
            # Update the drone's position based on mouse movement
            self.drone.current_location = (event.x - 15, event.y - 15)  # Center the drone on the mouse
            self.redraw_canvas()  # Redraw the canvas to update the drone's position
            
    def on_release_drone(self, event):
        if self.dragging:
            self.dragging = False  # Stop dragging

    def on_canvas_click(self, event):
        # Reset previous coordinates
        self.prev_x = event.x
        self.prev_y = event.y

        # Check for corner selection
        if self.check_for_corner_selection(event.x, event.y):
            self.resizing = True  # Indicate we are in resizing mode
            return  # Exit the method after resizing check

        # Check if clicking on the intruder
        if self.intruder and self.intruder.x <= event.x <= self.intruder.x + 50 and self.intruder.y <= event.y <= self.intruder.y + 90:
            self.dragging_intruder = self.intruder  # Set the dragging state
            return

        # Check if clicking on the drone
        if self.drone:
            drone_x, drone_y = self.drone.current_location  # Unpack current_location
            # Check if the click is within the bounds of the drone
            if drone_x <= event.x <= drone_x + 30 and drone_y <= event.y <= drone_y + 30:
                print("Drone clicked!")
                self.dragging = True  # Start dragging
        
        # Check if clicking on the panel
        if self.panel and self.panel.x <= event.x <= self.panel.x + 30 and self.panel.y <= event.y <= self.panel.y + 40:
            self.dragging_panel = self.panel  # Set the dragging state
            return

        # Check if clicking on a sensor
        for sensor in self.sensors:
            if sensor.x <= event.x <= sensor.x + 25 and sensor.y <= event.y <= sensor.y + 25:
                self.selected_sensor = sensor
                self.dragging_sensor = sensor
                return  # Exit if a sensor is selected

        # If no sensor, intruder, or drone is clicked, allow dragging the blueprint
        self.dragging = True


    def on_mouse_drag(self, event):
        # Check if dragging a sensor
        if self.dragging_sensor:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            self.dragging_sensor.x += dx
            self.dragging_sensor.y += dy
            self.redraw_canvas()  # Redraw canvas after moving sensor

        # Check if dragging an intruder
        elif self.dragging_intruder:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            self.dragging_intruder.x += dx
            self.dragging_intruder.y += dy
            self.redraw_canvas()  # Redraw canvas after moving intruder

        # Check if dragging a drone
        elif self.dragging_drone:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            self.dragging_drone.x += dx
            self.dragging_drone.y += dy
            self.redraw_canvas()  # Redraw canvas after moving drone
            
        # Check if dragging a panel
        elif self.dragging_panel:
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            self.dragging_panel.x += dx
            self.dragging_panel.y += dy
            self.redraw_canvas()  # Redraw canvas after moving panel

        # Check if resizing the blueprint
        elif self.resizing:
            self.resize_blueprint(event.x, event.y)
            self.prev_x = event.x
            self.prev_y = event.y

        # Check if dragging the blueprint
        elif self.dragging:  
            dx = event.x - self.prev_x
            dy = event.y - self.prev_y
            # Update blueprint position without affecting other images
            self.blueprint_position = (self.blueprint_position[0] + dx, self.blueprint_position[1] + dy)
            self.redraw_canvas()  # Redraw canvas to reflect blueprint movement
        
        # Update prev_x and prev_y regardless of action
        self.prev_x = event.x
        self.prev_y = event.y






    def on_mouse_release(self, event):
        # Reset dragging flags
        self.dragging_sensor = None
        self.dragging_intruder = None
        self.dragging_panel = None
        self.dragging_drone = None
        self.dragging = False
        self.resizing = False

        # Reset previous mouse position
        self.prev_x = None
        self.prev_y = None

        # Final redraw to ensure proper positioning
        self.redraw_canvas()



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

    
    def update_sensor_rotation(self, angle):
            if self.selected_sensor:
                # Update the selected sensor's angle and redraw the canvas
                self.selected_sensor.angle = float(angle)
                self.redraw_canvas()

    def open_panel_menu(self):
        # Create a top-level window for the panel menu
        menu_window = Toplevel(self.root)
        menu_window.title("Panel Menu")

        # Add a "Detect Sensors" button
        detect_btn = Button(menu_window, text="Detect Sensors", command=self.detect_sensors)
        detect_btn.pack()

        # "Send GPS to Drone" button (initially disabled)
        self.send_gps_btn = Button(menu_window, text="Send GPS to Drone", state=tk.DISABLED, command=self.send_gps_to_drone)
        self.send_gps_btn.pack()
        
    def open_panel_config(self):
        if not self.panel:
            messagebox.showinfo("No Panel", "Please add a panel before configuring.")
            return

        dialog = Toplevel(self.root)
        dialog.title("Configure Panel")

        # Panel Position Configuration
        tk.Label(dialog, text="Panel Position X:").pack()
        x_entry = tk.Entry(dialog)
        x_entry.pack()
        x_entry.insert(0, str(self.panel.x))

        tk.Label(dialog, text="Panel Position Y:").pack()
        y_entry = tk.Entry(dialog)
        y_entry.pack()
        y_entry.insert(0, str(self.panel.y))

        def save_config():
            self.panel.x = int(x_entry.get())
            self.panel.y = int(y_entry.get())
            dialog.destroy()
            self.redraw_canvas()  # Redraw to reflect changes

        # Save Button for Panel Configuration
        tk.Button(dialog, text="Save", command=save_config).pack()

        # Add "Detect Sensors" Button
        tk.Button(dialog, text="Detect Sensors", command=self.detect_sensors).pack()

        # "Send GPS to Drone" Button (Initially Disabled)
        self.send_gps_btn = tk.Button(dialog, text="Send GPS to Drone", state=tk.DISABLED, command=self.send_gps_to_drone)
        self.send_gps_btn.pack()


    def detect_sensors(self):
        # Simulate detecting sensors (this could be enhanced to detect actual sensors in the future)
        detected_sensors = [sensor for sensor in self.sensors if sensor.is_enabled]

        if not detected_sensors:
            messagebox.showinfo("No Sensors Detected", "No active sensors found.")
            return

        # Create a window to list detected sensors and assign GPS points
        sensors_window = Toplevel(self.root)
        sensors_window.title("Detected Sensors")

        for sensor in detected_sensors:
            sensor_label = tk.Label(sensors_window, text=sensor.name)
            sensor_label.pack()

            # Add a button to assign GPS points to each sensor
            gps_button = tk.Button(sensors_window, text="Add GPS Points", command=lambda s=sensor: self.add_gps_points(s))
            gps_button.pack()

        # Enable "Send GPS to Drone" after sensors are detected
        self.send_gps_btn.config(state=tk.NORMAL)

    def add_gps_points(self, sensor):
        # Open a window with an image to place GPS points
        gps_window = Toplevel(self.root)
        gps_window.title(f"Add GPS Points for {sensor.name}")

        gps_canvas = tk.Canvas(gps_window, width=400, height=400)
        gps_canvas.pack()

        # Load the gps.png image (assuming it's in the "static/images" directory)
        gps_image = tk.PhotoImage(file="static/images/gps.png")
        gps_canvas.create_image(0, 0, anchor=tk.NW, image=gps_image)

        # List of GPS points for this sensor
        self.gps_points[sensor.name] = []

        # When the user clicks on the image, record the GPS point
        def on_click(event):
            x, y = event.x, event.y
            print(f"GPS Point for {sensor.name}: ({x}, {y})")
            self.gps_points[sensor.name].append((x, y))

            # Optionally, draw markers on the canvas to represent points
            gps_canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")

        gps_canvas.bind("<Button-1>", on_click)

        # Add save button to finalize GPS points
        tk.Button(gps_window, text="Save", command=lambda: self.save_gps_points(sensor)).pack()

        
    def save_gps_points(self, sensor):
        # Save the GPS points for the sensor
        print(f"GPS Points saved for {sensor.name}: {self.gps_points[sensor.name]}")
        messagebox.showinfo("GPS Points Saved", f"GPS points for {sensor.name} have been saved.")


    def send_gps_to_drone(self):
        if self.drone:
            self.drone.receive_gps_points(self.gps_points)
            print("GPS points sent to drone.")
            messagebox.showinfo("Drone", "Signals received from drone.")
        else:
            messagebox.showinfo("Error", "No drone initialized.")
                
    
        
    def receive_gps_points(self, gps_points):
        # Simulate receiving GPS points (drone acknowledges receipt)
        print("Drone: GPS points received.")
        self.gps_points = gps_points
        self.scanning = True  # Enter listening mode

    def fly_to_sensor(self, sensor_gps_points):
        # Fly to each point associated with the triggered sensor
        for point in sensor_gps_points:
            self.current_location = point
            print(f"Drone flying to: {point}")
            self.scan_area()

    def scan_area(self):
        # Simulate scanning in a 6-meter radius
        radius = 6 * 50  # Convert meters to pixels (50 pixels per meter)
        print(f"Scanning area within {radius} pixels")

        # If intruder is within range, sound alarm
        if self.detect_intruder(radius):  # Pass the radius to detect_intruder method
            print("Intruder detected! Sounding alarm!")
            self.change_color()  # Change color to simulate alert
        else:
            print("No intruder detected.")


    def detect_intruder(self, scan_radius):
        if self.intruder:  # Check if there is an intruder to detect
            # Calculate distance between drone and intruder
            distance_to_intruder = math.sqrt(
                (self.intruder.x + 25 - self.current_location[0]) ** 2 + 
                (self.intruder.y + 45 - self.current_location[1]) ** 2
            )

            # Check if the distance is within the scan radius
            return distance_to_intruder <= scan_radius
        return False  # No intruder present or outside scan range


    def change_color(self):
        # Simulate the drone changing color to signal an alert
        print("Drone changing color to signal alarm.")
        
    def check_alarm(self):
        for sensor in self.sensors:
            if sensor.is_enabled:
                # Calculate detection range in pixels
                detection_range_pixels = sensor.detection_range * 50  # 50 pixels per meter
                sensor_center_x = sensor.x + 12.5
                sensor_center_y = sensor.y + 25  # Bottom of the sensor image

                if self.intruder:
                    # Log intruder position before calculation
                    print(f"Checking intruder position: ({self.intruder.x}, {self.intruder.y})")

                    # Calculate the distance to the intruder
                    distance_to_intruder = math.sqrt(
                        (self.intruder.x + 25 - sensor_center_x) ** 2 + 
                        (self.intruder.y + 45 - sensor_center_y) ** 2
                    )

                    # Log distance for debugging
                    print(f"Distance to intruder: {distance_to_intruder} pixels")

                    # Check if the intruder is within the sensor's FOV and range
                    if (distance_to_intruder <= detection_range_pixels and 
                        self.is_within_angle(sensor, self.intruder) and 
                        not sensor.triggered):  # Trigger only if not already triggered
                        sensor.triggered = True
                        print(f"Sensor {sensor.name} triggered! Distance: {distance_to_intruder}")
                        self.drone.fly_to_sensor(self.gps_points[sensor.name])
                    elif (distance_to_intruder > detection_range_pixels or 
                        not self.is_within_angle(sensor, self.intruder)):
                        sensor.triggered = False  # Reset trigger if out of range or angle
                else:
                    sensor.triggered = False  # Reset trigger if no intruder

    def simulate_intruder_detection(self):
        for sensor in self.sensors:
            if self.intruder_nearby(sensor):  # Check if the intruder is nearby
                if not sensor.triggered:  # Call check_alarm only if sensor isn't already triggered
                    self.check_alarm()
            else:
                sensor.triggered = False  # Reset the trigger if the intruder is not nearby

    def intruder_nearby(self, sensor):
        if self.intruder:  # Ensure there is an intruder to check
            # Calculate the distance between the sensor and the intruder
            distance_to_intruder = math.sqrt(
                (self.intruder.x + 25 - sensor.x) ** 2 + 
                (self.intruder.y + 45 - sensor.y) ** 2
            )
            # Return True if intruder is within the sensor's detection range
            return distance_to_intruder <= sensor.detection_range * 50  # 50 pixels per meter
        return False  # No intruder nearby

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorSimulationApp(root)
    root.mainloop()
