// Select the canvas and get the drawing context
const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');

// Define constants for sensor size and image
const sensorSize = 30; // Size in pixels
const sensorImage = new Image();
sensorImage.src = '/static/images/sensor.png'; // Load the sensor image

// Array to hold sensor data
let sensors = [];
let currentAngle = 0; // Current rotation angle
let draggingSensor = null; // Currently dragging sensor
let offsetX, offsetY; // Offset for dragging
let selectedSensor = null; // The currently selected sensor

// Function to draw a grid on the canvas
function drawGrid() {
    ctx.strokeStyle = 'lightgrey'; // Color of the grid lines
    ctx.lineWidth = 1; // Thickness of the grid lines
    
    // Draw vertical lines
  // Draw vertical lines every 50 pixels
  for (let x = 0; x <= canvas.width; x += 50) { // 50 pixels = 1 meter
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
}
    
    // Draw horizontal lines
    for (let y = 0; y <= canvas.height; y += 50) { // 50 pixels = 1 meter
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

// Function to draw a sensor on the canvas
function drawSensor(sensor) {
    ctx.save(); // Save the current context
    ctx.translate(sensor.x + sensorSize / 2, sensor.y + sensorSize / 2); // Center the sensor
    ctx.rotate(sensor.angle * Math.PI / 180); // Rotate based on the angle
    ctx.drawImage(sensorImage, -sensorSize / 2, -sensorSize / 2, sensorSize, sensorSize); // Draw the image
    ctx.restore(); // Restore the context to the previous state

    // If this sensor is selected, draw a green square around it
    if (sensor === selectedSensor) {
        ctx.strokeStyle = 'green'; // Green color for the border
        ctx.lineWidth = 3; // Border thickness
        ctx.strokeRect(sensor.x, sensor.y, sensorSize, sensorSize); // Draw the border
    }
}

// Load sensors from the server when the image is fully loaded
sensorImage.onload = async () => {
    await loadSensors(); // Load existing sensors when the image is ready
};

// Function to load existing sensors from the server
async function loadSensors() {
    const response = await fetch('/get_sensors');
    sensors = await response.json(); // Parse the JSON response
    redrawCanvas(); // Redraw the canvas after loading sensors
}

// Add event listener for adding sensors
document.getElementById('addSensorButton').addEventListener('click', (event) => {
    const newSensor = { x: Math.random() * (canvas.width - sensorSize), y: Math.random() * (canvas.height - sensorSize), angle: currentAngle };

    // Send sensor data to the server
    fetch('/add_sensor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSensor) // Send the sensor data as JSON
    }).then(() => {
        sensors.push(newSensor); // Add the new sensor to the local array
        redrawCanvas(); // Redraw the canvas to show the new sensor
    });
});

// Mouse down event for selecting and starting to drag sensors
canvas.addEventListener('mousedown', (event) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Check if a sensor is clicked
    sensors.forEach((sensor) => {
        if (
            mouseX >= sensor.x &&
            mouseX <= sensor.x + sensorSize &&
            mouseY >= sensor.y &&
            mouseY <= sensor.y + sensorSize
        ) {
            // Check if the selected sensor is already this sensor
            if (selectedSensor === sensor) {
                // Deselect if already selected
                selectedSensor = null; 
            } else {
                // Select this sensor
                selectedSensor = sensor; 
            }

            // Calculate the offset for dragging
            offsetX = mouseX - sensor.x;
            offsetY = mouseY - sensor.y;
            draggingSensor = sensor; // Start dragging this sensor

            redrawCanvas(); // Redraw the canvas
        }
    });
});

// Mouse move event for dragging sensors
canvas.addEventListener('mousemove', (event) => {
    if (draggingSensor) {
        const rect = canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        draggingSensor.x = mouseX - offsetX; // Update the sensor's x position
        draggingSensor.y = mouseY - offsetY; // Update the sensor's y position

        redrawCanvas(); // Redraw the canvas
    }
});

// Mouse up event to stop dragging
canvas.addEventListener('mouseup', () => {
    draggingSensor = null; // Reset the dragging sensor
});

// Mouse leave event to stop dragging
canvas.addEventListener('mouseleave', () => {
    draggingSensor = null; // Reset the dragging sensor
});

// Keydown event for deleting the selected sensor
document.addEventListener('keydown', (event) => {
    if (event.key === 'Delete' && selectedSensor) { // If 'Delete' key is pressed
        // Delete sensor from server
        fetch('/delete_sensor', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedSensor) // Send the sensor data as JSON
        }).then(() => {
            // Remove sensor from local array
            sensors = sensors.filter(sensor => sensor !== selectedSensor);
            selectedSensor = null; // Deselect the sensor
            redrawCanvas(); // Redraw the canvas
        });
    }
});

// Function to redraw the entire canvas
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    drawGrid(); // Draw the grid
    sensors.forEach(drawSensor); // Redraw all sensors
}

// Call the function to initialize the grid
drawGrid();
