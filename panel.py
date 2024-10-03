import tkinter as tk
from tkinter import ttk

class ControlPanel:
    def __init__(self, master, sensor_points):
        self.master = master
        self.sensor_points = sensor_points  # Dictionary to store sensor and points
        self.selected_sensor = tk.StringVar()  # To hold the selected sensor
        self.x_entry = tk.Entry(master)  # For X coordinate
        self.y_entry = tk.Entry(master)  # For Y coordinate
        self.point_list = []  # Store points for current sensor
        
        # Create the UI
        self.create_widgets()

    def create_widgets(self):
        # Dropdown to select sensor
        sensor_label = tk.Label(self.master, text="Select Sensor:")
        sensor_label.pack()

        sensor_options = ["Sensor 1", "Sensor 2", "Sensor 3"]  # Add more sensors as needed
        self.sensor_dropdown = ttk.Combobox(self.master, textvariable=self.selected_sensor, values=sensor_options)
        self.sensor_dropdown.pack()

        # Input fields for X and Y coordinates
        x_label = tk.Label(self.master, text="X Coordinate:")
        x_label.pack()
        self.x_entry.pack()

        y_label = tk.Label(self.master, text="Y Coordinate:")
        y_label.pack()
        self.y_entry.pack()

        # Button to add point
        add_point_button = tk.Button(self.master, text="Add Point", command=self.add_point)
        add_point_button.pack()

        # Listbox to display added points
        self.point_listbox = tk.Listbox(self.master)
        self.point_listbox.pack()

        # Save points button
        save_button = tk.Button(self.master, text="Save Points", command=self.save_points)
        save_button.pack()

    def add_point(self):
        # Get the X and Y values
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            point = (x, y)
            self.point_list.append(point)
            self.point_listbox.insert(tk.END, f"Point: {point}")
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)
        except ValueError:
            print("Please enter valid integer coordinates.")

    def save_points(self):
        # Get selected sensor and save points
        sensor = self.selected_sensor.get()
        if sensor:
            self.sensor_points[sensor] = self.point_list.copy()
            print(f"Points for {sensor}: {self.sensor_points[sensor]}")
            self.point_listbox.delete(0, tk.END)  # Clear listbox after saving
            self.point_list = []  # Clear the current point list
        else:
            print("Please select a sensor.")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sensor Control Panel")
    sensor_points = {}  # Dictionary to hold sensor points
    control_panel = ControlPanel(root, sensor_points)
    root.mainloop()

    print("Final Sensor Points:", sensor_points)
