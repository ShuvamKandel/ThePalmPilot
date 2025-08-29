import threading
import pyautogui
from pymongo import MongoClient
from threading import Lock
import time

# MongoDB connection and configuration
client = MongoClient("mongodb://localhost:27017")
db = client["motionDB"]  # Replace with your actual database name
collection = db["motionData"]  # Replace with your actual collection name

# Shared variables to store the coordinates and onOff status
shared_coordinates = {"X": 10, "Y": 10, "onOff": 0}
lock = Lock()

# Threshold for detecting significant movement
THRESHOLD = 4  # Change this value to adjust sensitivity

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
            shared_coordinates["onOff"] = data.get("onOff", shared_coordinates["onOff"])

def smooth_move_to(target_x, target_y, step=100, delay=0.005):
    """Move the cursor smoothly to the target coordinates."""
    current_x, current_y = pyautogui.position()
    step_x = step if target_x > current_x else -step
    step_y = step if target_y > current_y else -step

    # Gradual movement
    while abs(current_x - target_x) > abs(step_x) or abs(current_y - target_y) > abs(step_y):
        if abs(current_x - target_x) > abs(step_x):
            current_x += step_x
        if abs(current_y - target_y) > abs(step_y):
            current_y += step_y
        pyautogui.moveTo(current_x, current_y)
        time.sleep(delay)

    # Ensure final position is reached
    pyautogui.moveTo(target_x, target_y)

def perform_click(onOff):
    """Perform a left click if onOff is 1."""
    if onOff == 1:
        pyautogui.click()

def cursor_control():
    """Continuously move the cursor based on the latest coordinates and perform click if needed."""
    prev_x, prev_y = shared_coordinates["X"], shared_coordinates["Y"]
    
    while True:
        fetch_latest_data()  # Fetch the latest data from MongoDB
        with lock:
            x, y = shared_coordinates["X"], shared_coordinates["Y"]
            onOff = shared_coordinates["onOff"]
        
        # If the change in x or y is below the threshold, skip moving the cursor
        if abs(x - prev_x) < THRESHOLD and abs(y - prev_y) < THRESHOLD:
            continue
        
        mapped_x = map_value(x, 0, 250, 0, 2560)
        mapped_y = map_value(y, 0, 250, 0, 1260)
        
        print(f"Moving cursor to Mapped X: {mapped_x}, Mapped Y: {mapped_y}")
        smooth_move_to(mapped_x, mapped_y)  # Smoothly move the cursor to the mapped position
        
        # Perform click if onOff is 1
        perform_click(onOff)
        
        # Update previous coordinates for the next iteration
        prev_x, prev_y = x, y

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
