#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>

// Pin Definitions
int device1 = 25;
int device2 = 26;
int device3 = 27;
int device4 = 14;

bool myBoolValue;

// Firebase Configuration
#define WIFI_SSID "*****"
#define WIFI_PASSWORD "*****"
#define API_KEY "**********"
#define DATABASE_URL "**********"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// RF24 Setup
RF24 radio(4, 5); // CSN, CE pin
const uint64_t pipeIn = 0xE8E8F0F0E2LL;

// Data structure
struct sendData {
  byte sendX;
  byte sendY;
  byte sendZ;
  double sendLongitude;
  double sendLatitude;
};
sendData sData;

void setup() {
  pinMode(device1, OUTPUT);
  pinMode(device2, OUTPUT);
  pinMode(device3, OUTPUT);
  pinMode(device4, OUTPUT);

  Serial.begin(115200);
  radio.begin();
  radio.setAutoAck(false);
  radio.setDataRate(RF24_250KBPS);  
  radio.openReadingPipe(1, pipeIn);
  radio.startListening();

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
  delay(500);
  Serial.print(".");
  }
  Serial.println("Connected to Wi-Fi");


  // Firebase initialization
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  Firebase.begin(&config, &auth);

  if (!Firebase.signUp(&config, &auth, "", "")) {
  Serial.println("Firebase signup failed: " + fbdo.errorReason());

  }
}

void writeFirebaseData() {
  FirebaseJson json;
  json.set("X", sData.sendX);
  json.set("Y", sData.sendY);
  json.set("Z", sData.sendZ);
  
  if (Firebase.RTDB.updateNode(&fbdo, "/Data", &json)) {
    Serial.println("Data sent to Firebase");
  } else {
    Serial.println("Failed to send data to Firebase");
  }
}

void recvData() {
  if (radio.available()) {
    radio.read(&sData, sizeof(sData));
  }
}

void loop() {
  recvData();

  if (Firebase.RTDB.getBool(&fbdo, "/Data/switches")) {
    myBoolValue = fbdo.boolData();
  }

  if (myBoolValue == true){
    if (sData.sendX > 190) {
      digitalWrite(device4, LOW);
    } else if (sData.sendX < 50) {
      digitalWrite(device2, LOW);
    } else if (sData.sendY < 50) {
      digitalWrite(device1, LOW);
    } else if (sData.sendY > 200) {
      digitalWrite(device3, LOW);
    } else {
      digitalWrite(device1, HIGH);
      digitalWrite(device2, HIGH);
      digitalWrite(device3, HIGH);
      digitalWrite(device4, HIGH);
    }
  }
  writeFirebaseData();

  if (Firebase.RTDB.setFloat(&fbdo, "locations/user1/longitude", sData.sendLongitude)){
    Serial.println("PASSED");
    Serial.println("    PATH: " + fbdo.dataPath());
    Serial.println("TYPE: " + fbdo.dataType());
  }

  if (Firebase.RTDB.setFloat(&fbdo, "locations/user1/latitude", sData.sendLatitude)){
    Serial.println("PASSED");
    Serial.println("    PATH: " + fbdo.dataPath());
    Serial.println("TYPE: " + fbdo.dataType());
  }



}
