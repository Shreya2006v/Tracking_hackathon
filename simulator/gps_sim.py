import requests
import time
from datetime import datetime
import geopy.distance
import random

# ----------------- Configuration -----------------
BACKEND_URL = "http://127.0.0.1:5000/update_location"
UPDATE_INTERVAL = 5  # seconds
SPEED_MPS = 1  # Bus speed in meters/sec (~18 km/h)

# ----------------- Real-road routes in Chikkaballapur -----------------
routes = {
        "Route1": [[13.395494, 77.727767],[13.396575, 77.726641],[13.40636, 77.72726],[13.42360, 77.72973],[13.44748, 77.73556],[13.49102, 77.75213],[13.57671, 77.78114],[13.63116, 77.79161],[13.74052, 77.78955],[13.78286, 77.77496],[13.783176, 77.792923]],
    "Route2": [[13.396647, 77.726641],[13.406334, 77.727263],[13.435457, 77.731608],[13.43406, 77.73979],[13.42874, 77.76286],[13.42448, 77.77627],[13.41739, 77.79745],[13.41244, 77.80792],[13.39652, 77.82878],[13.38541, 77.84742],[13.38503, 77.85627],[13.38382, 77.86275],[13.384459, 77.862452]],
    "Route3": [[13.39571, 77.72660],[13.38324, 77.72625],[13.36013, 77.72561],[13.29839, 77.72574],[13.28382, 77.72286],[13.26904, 77.71994],[13.26368, 77.71797],[13.25825, 77.71398],[13.25044, 77.70686],[13.24956, 77.70861]]}

# ----------------- Assign buses -----------------


bus_routes = {
    "101": "Route1",
    "102": "Route1",
    "103": "Route2",
    "104": "Route2",
    "105": "Route3",
    "106": "Route3"
}
# Staggered start times (in seconds from script start)
bus_start_delays = {
    "101": 0,     # starts immediately
    "102": 20,    # starts after 20 seconds
    "103": 10,    # starts after 10 seconds
    "104": 30,    # starts after 30 seconds
    "105": 0,
    "106": 15
}
bus_start_times = {bus_id: time.time() + bus_start_delays.get(bus_id, 0) for bus_id in bus_routes}



# Track bus positions
bus_indices = {bus_id: 0 for bus_id in bus_routes}



# ----------------- ETA Calculation -----------------
def calculate_eta(route, index, speed_mps=SPEED_MPS):
    eta = 0
    for i in range(index, len(route)-1):
        point1 = route[i]
        point2 = route[i+1]
        dist = geopy.distance.geodesic(point1, point2).meters
        eta += dist / speed_mps
    return int(eta)

# ----------------- Main loop -----------------
while True:
    current_time = time.time()
    for bus_id, route_name in bus_routes.items():
        # Skip buses that haven't reached their start time
        if current_time < bus_start_times[bus_id]:
            continue

        route = routes[route_name]
        index = bus_indices[bus_id]

        print(f"Simulating bus {bus_id} on {route_name} at index {index}/{len(route)}")

        lat, lng = route[index]

        # Small random offset to prevent overlapping markers
        lat += random.uniform(-0.0002, 0.0002)
        lng += random.uniform(-0.0002, 0.0002)

        eta_sec = calculate_eta(route, index)

        data = {
            "bus_id": bus_id,
            "route": route_name,
            "lat": lat,
            "lng": lng,
            "timestamp": datetime.utcnow().isoformat(),
            "eta_seconds": eta_sec
        }

        try:
            response = requests.post(BACKEND_URL, json=data)
            if response.status_code == 200:
                print(f"Bus {bus_id} updated: {data}")
            else:
                print(f"Error updating {bus_id}: {response.text}")
        except Exception as e:
            print(f"Exception for {bus_id}: {e}")

        # Move to next point
        bus_indices[bus_id] = (index + 1) % len(route)

    time.sleep(UPDATE_INTERVAL)
