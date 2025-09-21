from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import math

app = Flask(__name__)
CORS(app)

# ----------------- In-memory storage -----------------
bus_locations = {}

# ----------------- Example bus stops in Chikkaballapur -----------------
bus_stops = {
    "Stop 1": {"lat": 13.3955, "lng": 77.7278},
    "Stop 2": {"lat": 13.4064, "lng": 77.7273},
    "Stop 3": {"lat": 13.4475, "lng": 77.7356},
    "Stop 4": {"lat": 13.5767, "lng": 77.7811},
    "Stop 5": {"lat": 13.7829, "lng": 77.7749}
}

AVERAGE_SPEED_KMPH = 18  # realistic bus speed (~5 m/s)

# ----------------- Utility Functions -----------------
def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def calculate_eta(bus_lat, bus_lng):
    """ETA (minutes) to each stop from current location."""
    eta_info = {}
    for stop, coords in bus_stops.items():
        dist_km = haversine(bus_lat, bus_lng, coords["lat"], coords["lng"])
        eta_min = (dist_km / AVERAGE_SPEED_KMPH) * 60
        eta_info[stop] = round(eta_min, 1)
    return eta_info

# ----------------- Routes -----------------
@app.route('/')
def home():
    return "🚍 Chikkaballapur Bus Tracking API is running!"

@app.route('/update_location', methods=['POST'])
def update_location():
    try:
        data = request.json
        bus_id = data.get("bus_id")
        route = data.get("route")
        lat = data.get("lat")
        lng = data.get("lng")
        eta_seconds = data.get("eta_seconds")  # from gps_sim.py

        if not all([bus_id, route, lat, lng]):
            return jsonify({"error":"bus_id, route, lat, lng are required"}),400

        # Calculate per-stop ETA
        per_stop_eta = calculate_eta(lat, lng)

        # Store all info
        bus_locations[bus_id] = {
            "bus_id": bus_id,
            "route": route,
            "lat": lat,
            "lng": lng,
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "eta_seconds": eta_seconds,
            "eta": per_stop_eta
        }

        return jsonify({"status":"updated", "bus_id": bus_id}),200

    except Exception as e:
        return jsonify({"error": str(e)}),500

@app.route('/bus_locations', methods=['GET'])
def get_locations():
    return jsonify(bus_locations)

# ----------------- Run Server -----------------
if __name__ == '__main__':
    app.run(debug=True)
