import pyrebase

# Firebase configuration (replace with your actual Firebase config)
firebaseConfig = {
    'apiKey': "AIzaSyDJFGpxt4NhJw_BICivqq9e84_VryR6vZk",
    'authDomain': "dinojump-5972c.firebaseapp.com",
    'databaseURL': "https://dinojump-5972c-default-rtdb.firebaseio.com",
    'projectId': "dinojump-5972c",
    'storageBucket': "dinojump-5972c.firebasestorage.app",
    'messagingSenderId': "373596765004",
    'appId': "1:373596765004:web:d375398c1269a677662de9"
}

# Initialize Pyrebase app
firebase = pyrebase.initialize_app(firebaseConfig)

# Get reference to the database
db = firebase.database()

# Function to monitor changes in X and update J accordingly
def update_j_based_on_x(x_value):
    try:
        # Set J to True if X is less than 100, else set J to False
        if x_value < 100:
            db.child("Data/J").set(True)
        else:
            db.child("Data/J").set(False)
    except Exception as e:
        print(f"Error: {e}")

# Stream handler that listens to changes in X
def stream_handler(message):
    # Extract the updated value of X from the message
    x_value = message['data']
    if x_value is not None:
        # Call the function to update J based on X
        update_j_based_on_x(x_value)

# Start streaming X changes in real-time
db.child("Data/X").stream(stream_handler)
