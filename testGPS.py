import pyrebase
import geocoder
import time  # To introduce a delay between location checks

# Pyrebase Configuration
config = {
    'apiKey': "AIzaSyDJFGpxt4NhJw_BICivqq9e84_VryR6vZk",
    'authDomain': "dinojump-5972c.firebaseapp.com",
    'databaseURL': "https://dinojump-5972c-default-rtdb.firebaseio.com",
    'projectId': "dinojump-5972c",
    'storageBucket': "dinojump-5972c.firebasestorage.app",
    'messagingSenderId': "373596765004",
    'appId': "1:373596765004:web:d375398c1269a677662de9"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Initialize previous location
previous_latitude = None
previous_longitude = None

# Continuously monitor location changes
while True:
    # Get Location Data (Using IP Geolocation)
    location = geocoder.ip('me')

    if location.ok:
        current_latitude = location.latlng[0]
        current_longitude = location.latlng[1]
        print(f"Current Latitude: {current_latitude}, Longitude: {current_longitude}")

        # Check if location has changed
        if (current_latitude != previous_latitude) or (current_longitude != previous_longitude):
            # Update the database
            data = {
                "latitude": current_latitude,
                "longitude": current_longitude,
            }
            db.child("locations").child("user1").set(data)
            print("Location updated in Firebase!")

            # Update previous location
            previous_latitude = current_latitude
            previous_longitude = current_longitude
        else:
            print("Location has not changed.")
    else:
        print("Could not determine location.")

    # Wait before checking again (adjust as needed)
    time.sleep(20)  # Check every 10 seconds
