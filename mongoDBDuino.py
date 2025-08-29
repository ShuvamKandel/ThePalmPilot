import threading
import pyautogui
from pymongo import MongoClient
from threading import Lock

# MongoDB connection and configuration
client = MongoClient("mongodb://localhost:27017")
db = client["motionDB"]  # Replace with your actual database name
collection = db["motionData"]  # Replace with your actual collection name

# Shared variables to store the coordinates
shared_coordinates = {"X": 10, "Y": 10}
lock = Lock()

def map_value(value, old_min, old_max, new_min, new_max):
    """Map a value from one range to another."""
    return new_min + ((value - old_min) * (new_max - new_min) / (old_max - old_min))

def fetch_latest_data():
    """Fetch the latest motion data from MongoDB."""
    global shared_coordinates
    # Get the most recent document from the collection (assuming a timestamp or order)
    latest_data = collection.find().sort("timestamp", -1).limit(1)
    for data in latest_data:
        with lock:
            shared_coordinates["X"] = data.get("x", shared_coordinates["X"])
            shared_coordinates["Y"] = data.get("y", shared_coordinates["Y"])

def smooth_move_to(target_x, target_y, step=100):
    """Move the cursor smoothly to the target coordinates without delay."""
    current_x, current_y = pyautogui.position()
    step_x = step if target_x > current_x else -step
    step_y = step if target_y > current_y else -step

    # Gradual movement without any sleep delay
    while abs(current_x - target_x) > abs(step_x) or abs(current_y - target_y) > abs(step_y):
        if abs(current_x - target_x) > abs(step_x):
            current_x += step_x
        if abs(current_y - target_y) > abs(step_y):
            current_y += step_y
        pyautogui.moveTo(current_x, current_y)

    # Ensure final position is reached
    pyautogui.moveTo(target_x, target_y)

def cursor_control():
    """Continuously move the cursor based on the latest coordinates without delay."""
    while True:
        fetch_latest_data()  # Fetch the latest data from MongoDB
        with lock:
            x, y = shared_coordinates["X"], shared_coordinates["Y"]
        mapped_x = map_value(x, 0, 255, 0, 2560)
        mapped_y = map_value(y, 0, 255, 0, 1260)
        print(f"Moving cursor to Mapped X: {mapped_x}, Mapped Y: {mapped_y}")
        smooth_move_to(mapped_x, mapped_y)

# Continuously fetch new data from MongoDB (polling) without delay
def start_data_polling():
    """Start the polling loop for MongoDB updates without delay."""
    while True:
        fetch_latest_data()  # Poll MongoDB for the latest data

# Start the cursor control loop in a separate thread
cursor_thread = threading.Thread(target=cursor_control, daemon=True)
cursor_thread.start()

# Start polling the database in the main thread
start_data_polling()
