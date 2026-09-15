import math
import serial
import time
import socket
import json
from collections import deque
from geographiclib.geodesic import Geodesic
from threading import Thread

# Function to calculate distance using GeographicLib
def calculate_distance(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    return geod.Inverse(lat1, lon1, lat2, lon2)['s12']

# Function to calculate bearing using GeographicLib
def calculate_bearing(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    azimuth = geod.Inverse(lat1, lon1, lat2, lon2)['azi1']
    return (azimuth + 360) % 360  # Normalize the bearing to 0-360 degrees

# Function to read GPS data from serial connection
def read_gps_data(serial_connection):
    try:
        line = serial_connection.readline().decode('utf-8').strip()
        if line.startswith("GPS,"):
            _, lat, lon = line.split(',')
            return float(lat), float(lon)
        return None, None
    except (ValueError, IndexError):
        print("Error parsing GPS data")
        return None, None

# Function to calculate moving average
def moving_average(values):
    return sum(values) / len(values) if values else 0

# Function to send commands to thrusters
def send_thruster_command(serial_connection, speeds):
    command = f"THR,{','.join(map(str, speeds))}\n"
    serial_connection.write(command.encode())
    # Wait for acknowledgment
    while True:
        response = serial_connection.readline().decode('utf-8').strip()
        if response.startswith("ACK,") or response.startswith("ERR,"):
            print(f"Arduino response: {response}")
            break

# Function to control thrusters based on navigation data
def control_thrusters(serial_connection, turn_angle, distance):
    # Thruster speed constants
    MAX_SPEED = 1800
    MIN_SPEED = 1100
    STOP_SPEED = 1500
    TURN_SPEED = 1700

    # Distance threshold for slowing down
    SLOW_DISTANCE = 10  # meters

    if distance < 2:
        # Stop all thrusters when destination is reached
        speeds = [STOP_SPEED] * 5
        print("Destination reached. Stopping all thrusters.")
    else:
        # Calculate forward speed based on distance
        forward_speed = MAX_SPEED if distance >= SLOW_DISTANCE else int(STOP_SPEED + (MAX_SPEED - STOP_SPEED) * (distance / SLOW_DISTANCE))

        if turn_angle < 10 or turn_angle > 350:
            # Go straight
            speeds = [forward_speed, forward_speed, STOP_SPEED, STOP_SPEED, STOP_SPEED]
            print("Going straight.")
        elif 10 <= turn_angle < 180:
            # Turn right
            speeds = [forward_speed, int(STOP_SPEED + (forward_speed - STOP_SPEED) * 0.5), STOP_SPEED, STOP_SPEED, TURN_SPEED]
            print(f"Turning right by {turn_angle:.2f} degrees.")
        elif 180 < turn_angle <= 350:
            # Turn left
            speeds = [int(STOP_SPEED + (forward_speed - STOP_SPEED) * 0.5), forward_speed, STOP_SPEED, STOP_SPEED, MIN_SPEED]
            print(f"Turning left by {360 - turn_angle:.2f} degrees.")
        else:
            # Heading away from destination, stop and turn
            speeds = [STOP_SPEED, STOP_SPEED, STOP_SPEED, STOP_SPEED, TURN_SPEED]
            print("Heading away from destination. Stopping and turning.")

    # Send the calculated speeds to the thrusters
    send_thruster_command(serial_connection, speeds)
    
class NavigationServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.client = None
        self.destination = None
        self.is_navigating = False
        # Comment out the serial connection for testing without Arduino
        self.arduino_serial = serial.Serial('COM4', baudrate=115200, timeout=1)  # Adjust port as needed

    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        self.socket.listen(1)
        while True:
            self.client, address = self.socket.accept()
            print(f"Connected to client: {address}")
            self.handle_client()

    def handle_client(self):
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if not data:
                    break
                command = json.loads(data)
                if command['type'] == 'set_destination':
                    self.destination = (command['lat'], command['lon'])
                    self.client.send(json.dumps({'status': 'Destination set'}).encode('utf-8'))
                elif command['type'] == 'start_navigation':
                    self.is_navigating = True
                    Thread(target=self.navigate).start()
                    self.client.send(json.dumps({'status': 'Navigation started'}).encode('utf-8'))
                elif command['type'] == 'stop_navigation':
                    self.is_navigating = False
                    self.client.send(json.dumps({'status': 'Navigation stopped'}).encode('utf-8'))
            except json.JSONDecodeError:
                print("Invalid JSON received")
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        self.client.close()

    def navigate(self):
        lat_history = deque(maxlen=5)
        lon_history = deque(maxlen=5)
        heading_history = deque(maxlen=5)
        prev_lat, prev_lon = None, None
        current_heading = None
        min_movement_threshold = 1  # meters

        while self.is_navigating:
            # Comment out the serial connection for testing without Arduino
            current_lat, current_lon = read_gps_data(self.arduino_serial)
            #current_lat, current_lon = 31.835928, 54.354836  # Dummy data for testing
            if current_lat is None or current_lon is None:
                print("Error reading GPS data. Skipping this iteration.")
                #time.sleep(1)
                continue

            lat_history.append(current_lat)
            lon_history.append(current_lon)

            smoothed_lat = moving_average(lat_history)
            smoothed_lon = moving_average(lon_history)

            distance = calculate_distance(smoothed_lat, smoothed_lon, self.destination[0], self.destination[1])
            bearing_to_destination = calculate_bearing(smoothed_lat, smoothed_lon, self.destination[0], self.destination[1])

            if prev_lat is not None and prev_lon is not None:
                movement = calculate_distance(prev_lat, prev_lon, smoothed_lat, smoothed_lon)
                
                if movement > min_movement_threshold:
                    new_heading = calculate_bearing(prev_lat, prev_lon, smoothed_lat, smoothed_lon)
                    heading_history.append(new_heading)
                    current_heading = moving_average(heading_history)
                    prev_lat, prev_lon = smoothed_lat, smoothed_lon
                else:
                    print("No significant movement detected.")

                if current_heading is not None:
                    turn_angle = (bearing_to_destination - current_heading + 360) % 360

                    status = {
                        'lat': smoothed_lat,
                        'lon': smoothed_lon,
                        'heading': current_heading,
                        'bearing': bearing_to_destination,
                        'turn_angle': turn_angle,
                        'distance': distance
                    }
                    self.client.send(json.dumps(status).encode('utf-8'))

                    # Comment out the serial connection for testing without Arduino
                    control_thrusters(self.arduino_serial, turn_angle, distance)

                    if distance < 2:
                        print("Destination reached!")
                        self.is_navigating = False
                        break
            else:
                prev_lat, prev_lon = smoothed_lat, smoothed_lon

            #time.sleep(1)

        # Stop all thrusters when navigation is complete or stopped
        # Comment out the serial connection for testing without Arduino
        #send_thruster_command(self.arduino_serial, [1500, 1500, 1500, 1500, 1500])

if __name__ == "__main__":
    server = NavigationServer()
    server.start()
