from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory storage for sensors (for demonstration purposes)
sensors = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    sensor_data = request.get_json()
    sensors.append(sensor_data)
    return jsonify(sensor_data), 201

@app.route('/delete_sensor', methods=['DELETE'])
def delete_sensor():
    sensor_data = request.get_json()
    global sensors
    sensors = [sensor for sensor in sensors if not (sensor['x'] == sensor_data['x'] and sensor['y'] == sensor_data['y'])]
    return jsonify({'status': 'deleted'}), 204

@app.route('/get_sensors', methods=['GET'])
def get_sensors():
    return jsonify(sensors)

if __name__ == '__main__':
    app.run(debug=True)
