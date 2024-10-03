// Select the canvas and get the drawing context
const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');

// Define constants for sensor properties and grid
const sensorSize = 30; // Size in pixels
const gridSize = 50; // 1 meter = 50 pixels
const sensorImage = new Image();
sensorImage.src = '/static/images/sensor.png'; // Default sensor image

// Array to hold all sensors
let sensors = [];

let offsetX, offsetY; // For dragging offset
let selectedSensor = null; // Sensor currently selected

// Draw grid function
function drawGrid() {
    ctx.strokeStyle = 'lightgrey';
    ctx.lineWidth = 1;
    
    // Draw vertical grid lines
    for (let x = 0; x <= canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    
    // Draw horizontal grid lines
    for (let y = 0; y <= canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

// Function to draw a single sensor
function drawSensor(sensor) {
    ctx.save(); // Save the current context state
    ctx.translate(sensor.x + sensorSize / 2, sensor.y + sensorSize / 2); // Center the sensor
    ctx.rotate(sensor.angle * Math.PI / 180); // Rotate the sensor based on its angle

    // Load the appropriate sensor image
    const imageToUse = new Image();
imageToUse.src = sensor.isEnabled ? '/static/images/sensor_on.png' : '/static/images/sensor.png';

    
    // Draw the sensor image
    ctx.drawImage(imageToUse, -sensorSize / 2, -sensorSize / 2, sensorSize, sensorSize);

    // Draw a green border if selected
    if (sensor === selectedSensor) {
        ctx.strokeStyle = 'green';
        ctx.lineWidth = 3;
        ctx.strokeRect(-sensorSize / 2, -sensorSize / 2, sensorSize, sensorSize);
    }

    ctx.restore(); // Restore the previous context state
}

// Function to redraw the entire canvas
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    drawGrid(); // Redraw the grid
    sensors.forEach(drawSensor); // Draw all sensors
    sensors.forEach(drawFieldOfView); // Draw field of view for each sensor
}

// Function to draw the field of view for a sensor
function drawFieldOfView(sensor) {
    if (sensor.detectionRange <= 0 || sensor.detectionAngle <= 0) return; // Exit if no range or angle

    ctx.save();
    ctx.translate(sensor.x + sensorSize / 2, sensor.y + sensorSize); // Base of the sensor
    ctx.rotate(sensor.angle * Math.PI / 180); // Rotate based on the angle

    ctx.fillStyle = 'rgba(0, 255, 0, 0.5)'; // Semi-transparent green for field of view
    ctx.beginPath();
    ctx.moveTo(0, 0); // Start at sensor

    const halfAngle = sensor.detectionAngle / 2;
    const rangeInPixels = sensor.detectionRange * gridSize; // Convert range from meters to pixels

    // Draw the left edge of the field of view
    ctx.lineTo(
        rangeInPixels * Math.cos(-halfAngle * Math.PI / 180),
        -rangeInPixels * Math.sin(-halfAngle * Math.PI / 180)
    );

    // Draw the right edge of the field of view
    ctx.lineTo(
        rangeInPixels * Math.cos(halfAngle * Math.PI / 180),
        -rangeInPixels * Math.sin(halfAngle * Math.PI / 180)
    );

    ctx.closePath(); // Complete the wedge shape
    ctx.fill(); // Fill the wedge
    ctx.restore(); // Restore context
}

// Function to add a new sensor
function addSensor() {
    const newSensor = {
        x: Math.random() * (canvas.width - sensorSize),
        y: Math.random() * (canvas.height - sensorSize),
        angle: 0,
        detectionRange: 0, // Default detection range
        detectionAngle: 0, // Default detection angle
        isEnabled: false, // Default is off
        name: '', // Default name
    };

    // Save the sensor to the server
    fetch('/add_sensor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSensor)
    }).then(() => {
        sensors.push(newSensor); // Add sensor locally
        redrawCanvas(); // Redraw canvas with new sensor
    });
}

// Function to open sensor configuration popup
function showSensorConfig(sensor) {
    const popup = document.getElementById('sensorConfigPopup');
    document.getElementById('sensorName').value = sensor.name;
    document.getElementById('detectionRange').value = sensor.detectionRange;
    document.getElementById('detectionAngle').value = sensor.detectionAngle;

    document.getElementById('toggleSensorButton').onclick = () => {
        sensor.isEnabled = !sensor.isEnabled; // Toggle sensor state
        redrawCanvas();
    };

    document.getElementById('saveSensorButton').onclick = () => {
        sensor.name = document.getElementById('sensorName').value;
        sensor.detectionRange = parseFloat(document.getElementById('detectionRange').value);
        sensor.detectionAngle = parseFloat(document.getElementById('detectionAngle').value);

        // Update sensor on the server
        fetch('/update_sensor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sensor)
        }).then(() => {
            redrawCanvas();
            popup.style.display = 'none';
        });
    };

    document.getElementById('exitConfigButton').onclick = () => {
        popup.style.display = 'none';
    };

    popup.style.display = 'block'; // Show the popup
}

// Mouse down event to select or drag sensor
canvas.addEventListener('mousedown', (event) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    sensors.forEach((sensor) => {
        if (
            mouseX >= sensor.x &&
            mouseX <= sensor.x + sensorSize &&
            mouseY >= sensor.y &&
            mouseY <= sensor.y + sensorSize
        ) {
            if (selectedSensor === sensor) {
                showSensorConfig(sensor); // Open config if sensor is clicked again
            } else {
                selectedSensor = sensor; // Select this sensor
            }

            offsetX = mouseX - sensor.x; // Calculate offset for dragging
            offsetY = mouseY - sensor.y;
            draggingSensor = sensor; // Set dragging state

            redrawCanvas();
        }
    });
});

// Mouse move event for dragging sensors
canvas.addEventListener('mousemove', (event) => {
    if (draggingSensor) {
        const rect = canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        draggingSensor.x = mouseX - offsetX;
        draggingSensor.y = mouseY - offsetY;

        redrawCanvas();
    }
});

// Mouse up event to stop dragging
canvas.addEventListener('mouseup', () => {
    draggingSensor = null;
});

// Mouse leave event to stop dragging when leaving the canvas
canvas.addEventListener('mouseleave', () => {
    draggingSensor = null;
});

// Delete sensor with the 'Delete' key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Delete' && selectedSensor) {
        fetch('/delete_sensor', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedSensor)
        }).then(() => {
            sensors = sensors.filter(sensor => sensor !== selectedSensor); // Remove from local array
            selectedSensor = null; // Clear selection
            redrawCanvas();
        });
    }
});

// Initial load of sensors from the server
function loadSensors() {
    fetch('/get_sensors')
        .then(response => response.json())
        .then(data => {
            sensors = data; // Load sensors into the local array
            redrawCanvas(); // Redraw the canvas with the loaded sensors
        });
}

// Load sensors and set initial canvas state
sensorImage.onload = loadSensors;

// Attach add sensor button functionality
document.getElementById('addSensorButton').addEventListener('click', addSensor);

// Function to add a sensor to the canvas
function addSensor() {
    const newSensor = {
        x: Math.random() * (canvas.width - sensorSize),
        y: Math.random() * (canvas.height - sensorSize),
        angle: 0,
        detectionRange: 0, // Default detection range
        detectionAngle: 0, // Default detection angle
        isEnabled: false,   // Default is off
        name: '',           // Default name
    };

    // Save the sensor to the server
    fetch('/add_sensor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSensor)
    }).then(() => {
        sensors.push(newSensor); // Add sensor to local array
        redrawCanvas();          // Redraw canvas with the new sensor
    });
}

// Function to redraw the entire canvas (grid, sensors, FOV)
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas
    drawGrid();                                       // Redraw grid
    sensors.forEach(drawSensor);                      // Draw each sensor
    sensors.forEach(drawFieldOfView);                 // Draw the FOV for each sensor
}

// Function to draw the grid on the canvas
function drawGrid() {
    const gridSpacing = 50; // 1 meter by 1 meter grid

    ctx.strokeStyle = '#ddd';
    for (let x = 0; x <= canvas.width; x += gridSpacing) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }

    for (let y = 0; y <= canvas.height; y += gridSpacing) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

// Function to draw a sensor on the canvas
function drawSensor(sensor) {
    const sensorImage = new Image();
    sensorImage.src = sensor.isEnabled ? 'images/sensor_on.png' : 'images/sensor.png';
    sensorImage.onload = function() {
        ctx.save();
        ctx.translate(sensor.x + sensorSize / 2, sensor.y + sensorSize / 2);
        ctx.rotate(sensor.angle * Math.PI / 180);
        ctx.drawImage(sensorImage, -sensorSize / 2, -sensorSize / 2, sensorSize, sensorSize);
        ctx.restore();
    };
}

// Function to draw the field of view (FOV) for each sensor
function drawFieldOfView(sensor) {
    if (sensor.detectionRange > 0 && sensor.detectionAngle > 0) {
        const fovStartAngle = (sensor.angle - sensor.detectionAngle / 2) * (Math.PI / 180);
        const fovEndAngle = (sensor.angle + sensor.detectionAngle / 2) * (Math.PI / 180);

        ctx.save();
        ctx.translate(sensor.x + sensorSize / 2, sensor.y + sensorSize / 2);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, sensor.detectionRange, fovStartAngle, fovEndAngle);
        ctx.closePath();
        ctx.fillStyle = 'rgba(200, 200, 200, 0.5)';
        ctx.fill();
        ctx.restore();
    }
}

// Function to handle double-click on sensor to open configuration popup
canvas.addEventListener('dblclick', function(event) {
    const clickedSensor = sensors.find(sensor => isSensorClicked(sensor, event.offsetX, event.offsetY));
    if (clickedSensor) {
        openSensorConfig(clickedSensor);
    }
});

// Function to check if a sensor was clicked
function isSensorClicked(sensor, x, y) {
    return x >= sensor.x && x <= sensor.x + sensorSize &&
           y >= sensor.y && y <= sensor.y + sensorSize;
}

// Function to open the sensor configuration popup
function openSensorConfig(sensor) {
    const configPopup = document.getElementById('sensorConfigPopup');
    const sensorNameInput = document.getElementById('sensorName');
    const detectionRangeInput = document.getElementById('detectionRange');
    const detectionAngleInput = document.getElementById('detectionAngle');
    const sensorToggleButton = document.getElementById('sensorToggleButton');

    // Set popup inputs to the sensor's current values
    sensorNameInput.value = sensor.name;
    detectionRangeInput.value = sensor.detectionRange;
    detectionAngleInput.value = sensor.detectionAngle;
    sensorToggleButton.textContent = sensor.isEnabled ? 'Turn Off' : 'Turn On';

    // Show the popup
    configPopup.style.display = 'block';

    // Save button click handler
    document.getElementById('saveSensorConfig').onclick = function() {
        sensor.name = sensorNameInput.value;
        sensor.detectionRange = parseFloat(detectionRangeInput.value);
        sensor.detectionAngle = parseFloat(detectionAngleInput.value);

        // Hide the popup and redraw the canvas
        configPopup.style.display = 'none';
        redrawCanvas();
    };

    // Toggle sensor on/off button handler
    sensorToggleButton.onclick = function() {
        sensor.isEnabled = !sensor.isEnabled;
        sensorToggleButton.textContent = sensor.isEnabled ? 'Turn Off' : 'Turn On';
        redrawCanvas(); // Redraw the canvas to update sensor image
    };

    // Exit button click handler
    document.getElementById('exitSensorConfig').onclick = function() {
        configPopup.style.display = 'none';
    };
}

// Function to handle dragging sensors
let draggingSensor = null;
canvas.addEventListener('mousedown', function(event) {
    draggingSensor = sensors.find(sensor => isSensorClicked(sensor, event.offsetX, event.offsetY));
});

canvas.addEventListener('mousemove', function(event) {
    if (draggingSensor) {
        draggingSensor.x = event.offsetX - sensorSize / 2;
        draggingSensor.y = event.offsetY - sensorSize / 2;
        redrawCanvas();
    }
});

canvas.addEventListener('mouseup', function() {
    draggingSensor = null;
});
