import pyrebase
import pyautogui
import threading
import time

# Firebase configuration and initialization
firebaseConfig = {
    'apiKey': "AIyaSyDJFGpxt4NhJw_BICivqq9e84_VryR6vYk",
    'authDomain': "dinojump-5972c.firebaseapp.com",
    'databaseURL': "https://dinojump-5972c-default-rtdb.firebaseio.com",
    'projectId': "dinojump-5972c",
    'storageBucket': "dinojump-5972c.firebasestorage.app",
    'messagingSenderId': "373596765004",
    'appId': "1:373596765004:web:d375398c1269a677662de9"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Shared variables to store the coordinates
shared_coordinates = {"X": 10, "Y": 10}
lock = threading.Lock()

def map_value(value, old_min, old_max, new_min, new_max):
    """Map a value from one range to another."""
    return new_min + ((value - old_min) * (new_max - new_min) / (old_max - old_min))

def stream_handler(message):
    """Handle real-time updates from Firebase."""
    global shared_coordinates
    if message["event"] in ("put", "patch"):  # Data was updated
        data = message["data"]
        if isinstance(data, dict):
            with lock:
                shared_coordinates["X"] = data.get("X", shared_coordinates["X"])
                shared_coordinates["Y"] = data.get("Y", shared_coordinates["Y"])
        elif isinstance(data, (int, float)):  # Handle direct value updates (unlikely in this case)
            with lock:
                if message["path"] == "/X":
                    shared_coordinates["X"] = data
                elif message["path"] == "/Y":
                    shared_coordinates["Y"] = data

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

def cursor_control():
    """Continuously move the cursor based on the latest coordinates."""
    while True:
        with lock:
            x, y = shared_coordinates["X"], shared_coordinates["Y"]
        mapped_x = map_value(x, 0, 255, 0, 2560)
        mapped_y = map_value(y, 0, 255, 0, 1260)
        print(f"Moving cursor to Mapped X: {mapped_x}, Mapped Y: {mapped_y}")
        smooth_move_to(mapped_x, mapped_y)
        time.sleep(0.05)  # Small delay to avoid excessive CPU usage

# Set up the real-time listener for Firebase updates
def setup_stream():
    """Start the Firebase real-time database stream."""
    try:
        db.child("Data").stream(stream_handler)
    except Exception as e:
        print(f"Error setting up stream: {e}")

# Start the cursor control loop
cursor_thread = threading.Thread(target=cursor_control, daemon=True)
cursor_thread.start()

# Start the Firebase stream in the main thread
setup_stream()