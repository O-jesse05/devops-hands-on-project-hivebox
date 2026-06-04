from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
from statistics import mean
import os

app = Flask(__name__)

# Configuration
OPEN_SENSEMAP_API = "https://api.opensensemap.org"
APP_VERSION = "1.0.0"

def get_recent_temperature_measurements():
    """Fetch recent temperature measurements from openSenseMap"""
    temperatures = []
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    
    try:
        response = requests.get(
            f"{OPEN_SENSEMAP_API}/boxes",
            params={'limit': 100},
            timeout=10
        )
        
        if response.status_code != 200:
            return temperatures
        
        boxes = response.json()
        
        for box in boxes:
            sensors = box.get('sensors', [])
            for sensor in sensors:
                unit = sensor.get('unit', '').lower()
                if unit == '°c' or 'temp' in sensor.get('title', '').lower():
                    last_measurement = sensor.get('lastMeasurement')
                    if last_measurement and 'value' in last_measurement:
                        created_at = last_measurement.get('createdAt')
                        if created_at:
                            try:
                                if created_at.endswith('Z'):
                                    created_at = created_at[:-1] + '+00:00'
                                measurement_time = datetime.fromisoformat(created_at)
                                if measurement_time.tzinfo:
                                    measurement_time = measurement_time.replace(tzinfo=None)
                                
                                if measurement_time >= cutoff_time:
                                    temp_value = float(last_measurement['value'])
                                    if -40 <= temp_value <= 60:
                                        temperatures.append(temp_value)
                            except (ValueError, TypeError):
                                continue
    except requests.RequestException as e:
        print(f"Error: {e}")
    
    return temperatures

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Temperature API is running',
        'endpoints': {
            'version': '/version',
            'temperature': '/temperature',
            'health': '/health'
        },
        'documentation': 'Use GET requests to access these endpoints'
    })

@app.route('/version', methods=['GET'])
def get_version():
    """Return the version of the app"""
    return jsonify({
        'version': APP_VERSION,
        'service': 'Temperature API',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/temperature', methods=['GET'])
def get_temperature():
    """Return average temperature from recent sensor data"""
    temperatures = get_recent_temperature_measurements()
    
    if not temperatures:
        return jsonify({
            'error': 'No recent temperature data available',
            'message': 'No measurements found from the last hour',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 404
    
    average_temp = mean(temperatures)
    
    return jsonify({
        'average_temperature': round(average_temp, 2),
        'unit': 'celsius',
        'sample_size': len(temperatures),
        'time_window_hours': 1,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
