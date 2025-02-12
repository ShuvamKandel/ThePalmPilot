#include <BleMouse.h>
#include <Wire.h>
#include <MPU6050.h>

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#include <TinyGPSPlus.h>

MPU6050 mpu;
BleMouse bleMouse;

RF24 radio(27, 5);

// Set the ESP32 pins for the GPS module (adjust as needed)
static const int RXPin = 16;  // Connect GPS TX to ESP32 GPIO16
static const int TXPin = 17;  // Connect GPS RX to ESP32 GPIO17 (if needed)
static const uint32_t GPSBaud = 9600;  // Adjust if your GPS uses a different baud rate

TinyGPSPlus gps;
HardwareSerial gpsSerial(2);  // Using UART2 on ESP32

double latitude;
double longitude;


float sensitivityAccel = 16384.0;
float cursorSpeedX = 8.0;  
float cursorSpeedY = 8.0;  
float motionThreshold = 0.1;

int touchPinClick = T0;
int touchPinCar = T9;

int touchValueClick = 0;
bool onOffClick = 0;

int touchValueCar = 0;
bool onOffCar = 0;


struct sendData {
  byte sendX, sendY, sendZ, sendT;
  double sendLongitude, sendLatitude;
};

sendData sData;

const uint64_t pipeOut = 0xE8E8F0F0E1LL;
const uint64_t address2 = 0xE8E8F0F0E2LL;


unsigned long clickStartTime = 0;
const unsigned long clickDelay = 500;

void resetData() {
  memset(&sData, 0, sizeof(sendData));
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
    mpu.initialize();
    if (!mpu.testConnection()) while (1);
    mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_500);
    bleMouse.begin();

    pinMode(touchPinClick, INPUT);
    pinMode(touchPinCar, INPUT);

    radio.begin();
    radio.setAutoAck(false);
    radio.stopListening();
    radio.setDataRate(RF24_250KBPS);
    resetData();

    gpsSerial.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);
    Serial.println("GPS Reader Starting...");

}

void loop() {

    while (gpsSerial.available() > 0) {
      gps.encode(gpsSerial.read());
    }

    if (gps.location.isValid()) {
      latitude = gps.location.lat();
      longitude = gps.location.lng();
      Serial.print("Latitude: ");
      Serial.print(latitude, 6);  // 6 decimal places
      Serial.print("  Longitude: ");
      Serial.println(longitude, 6);
    } else {
      Serial.println("Waiting for GPS fix...");
    }

    touchValueClick = touchRead(touchPinClick);
    onOffClick = (touchValueClick < 20);

    touchValueCar = touchRead(touchPinCar);
    onOffCar = (touchValueCar < 20);

    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);

    sData.sendX = map(ax, -17000, 17000, 0, 255);
    sData.sendY = map(ay, -17000, 17000, 0, 255);
    sData.sendZ = map(az, -17000, 17000, 0, 255);
    sData.sendT = mpu.getTemperature() / 340.0 + 36.53;
    sData.sendLatitude = latitude;
    sData.sendLongitude = longitude;

    if (onOffCar == true){
      radio.openWritingPipe(pipeOut);
      radio.write(&sData, sizeof(sData));
      onOffCar = false;
    }
    else{
      radio.openWritingPipe(address2);
      radio.write(&sData, sizeof(sData));
    }

    if (onOffClick) {
        if (clickStartTime == 0) {
            clickStartTime = millis();
        }
        else if (millis() - clickStartTime >= clickDelay) {
            if (bleMouse.isConnected()) {
                bleMouse.click(MOUSE_LEFT);
                clickStartTime = 0;
            }
        }
    }
    else {
        clickStartTime = 0;
    }

    if (bleMouse.isConnected()) {
      float accelX = ax / sensitivityAccel;
      float accelY = ay / sensitivityAccel;

      if (abs(accelX) > motionThreshold || abs(accelY) > motionThreshold) {
          bleMouse.move(accelX * cursorSpeedX, accelY * cursorSpeedY);
      }
    }
}