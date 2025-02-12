# The Palm Pilot
This is a device that can control any laptop's cursor and move a RC car with the motion of the hand.

## Making the Transmitter module
The NRF24 module's serial comminication pins need to be connected to thier usual pins on the esp32. CE and CSN go to pins 4 and 27.
MPU6050 SCL and SDA also go to their usual pins.
Connecting the GPS module is optional as it was kept for another functionality which becomes irrelevant in this project.

## Making the RC Car
Connect the ENA, ENB, AIN1, AIN2, BIN1, BIN2 pins to the L298N motor driver according to the 'motionCar.ino' code
The NRF24 module's serial comminication pins need to be connected to thier usual pins on the esp32. CE and CSN go to pins 4 and 5, check the code for further clarification.


## Setting up bluetooth
Open bluetooth settings on your device. Go to configure a bluetooth mouse and you will see the ESP32 pop up. Connect the bluetooth. Now, as you move the motion sensor, the cursor should move.
