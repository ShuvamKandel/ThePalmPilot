#include <SPI.h>
#include <nRF24L01.h>             
#include <RF24.h>

// Motor driver pins (adjust accordingly)
#define IN1 21
#define IN2 22
#define IN3 14
#define IN4 25
#define ENA 26
#define ENB 27

const uint64_t pipeIn = 0xE8E8F0F0E1LL;

RF24 radio(4, 5); //CSN and CE
struct sendData {
  byte sendX;
  byte sendY;
  byte sendZ;
  byte sendFlex;
};
sendData sData;

void resetData() 
{
  sData.sendX = 0;
  sData.sendY = 0;
  sData.sendZ = 0;
  sData.sendFlex = 0;  
}

int x = 0;
int y = 0;


// Motor control pins setup
void setupMotors() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  analogWrite(ENA, 135); // Full speed
  analogWrite(ENB, 135); // Full speed
}

void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void stopCar() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void setup() {
  Serial.begin(115200);

  // Setup motors
  setupMotors();

  // Connect to Wi-Fi
  resetData();
  radio.begin();
  radio.setAutoAck(false);
  radio.setDataRate(RF24_250KBPS);  
  radio.openReadingPipe(1,pipeIn);
  //we start the radio comunication
  radio.startListening();

}
unsigned long lastRecvTime = 0;

void recvData()
{
  while ( radio.available() )
  {
    radio.read(&sData, sizeof(sendData));
    lastRecvTime = millis();
  }
}

void loop() {
  recvData();
  unsigned long now = millis();

  if ( now - lastRecvTime > 1000 ) {
  resetData();
  }

  Serial.print("Axis X = ");
  Serial.print(sData.sendX);
  Serial.print("  ");
  Serial.print("Axis Y = ");
  Serial.print(sData.sendY);
  Serial.print("  ");
  Serial.print("Axis Z  = ");
  Serial.println(sData.sendZ);

  x = sData.sendX;
  y = sData.sendY;

  // Control car based on X and Y values
  if(x == 0 && y == 0){
    stopCar();
  }
  else{
    controlMotors();
  }

}

// X-axis control (turning left/right)

// Y-axis control (moving forward/backward)
void controlMotors() {
  if (y < 100) {
    moveForward();
    Serial.println("Moving Forward");
  } else if (y > 200) {
    moveBackward();
    Serial.println("Moving Backward");
  } else if (x < 100) {
    turnLeft();
    Serial.println("Turning Left");
  } else if (x > 200) {
    turnRight();
    Serial.println("Turning Right");
  } else {
    stopCar();
    Serial.println("Stopped");
  }
}