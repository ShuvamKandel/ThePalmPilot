#include <NewPing.h>
#include <ESP32Servo.h>

// Pin definitions
#define TRIG_PIN 25   // Trigger pin of the ultrasonic sensor
#define ECHO_PIN 26   // Echo pin of the ultrasonic sensor
#define MAX_DISTANCE 200 // Maximum distance to measure (in cm)
#define SERVO_PIN 15  // Servo motor control pin
#define BUZZER_PIN 8 // Buzzer control pin

// Create objects for ultrasonic sensor and servo motor
NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);
Servo myServo;

// Distance threshold (in cm)
const int DISTANCE_THRESHOLD = 10;

// Initial servo position
const int SERVO_INITIAL_POSITION = 0;
const int SERVO_ACTIVATED_POSITION = 90;

// Timing variables for buzzer control
unsigned long previousMillis = 0;
const unsigned long BUZZER_INTERVAL = 15000; // 15 seconds

void setup() {
  Serial.begin(9600); // Start serial communication
  myServo.attach(SERVO_PIN); // Attach the servo motor
  myServo.write(SERVO_INITIAL_POSITION); // Set servo to initial position
  pinMode(BUZZER_PIN, OUTPUT); // Set buzzer pin as output
  digitalWrite(BUZZER_PIN, LOW); // Ensure the buzzer starts off
}

void loop() {
  unsigned long currentMillis = millis(); // Get current time
  int distance = sonar.ping_cm(); // Measure distance in cm

  // Print distance to Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Check distance and control the servo
  if (distance > 0 && distance <= DISTANCE_THRESHOLD) {
    myServo.write(SERVO_ACTIVATED_POSITION); // Turn servo 90 degrees
    digitalWrite(BUZZER_PIN, LOW); // Turn off buzzer if object is detected
  } else {
    myServo.write(SERVO_INITIAL_POSITION); // Return servo to initial position

    // Control buzzer with 15-second intervals
    if (currentMillis - previousMillis >= BUZZER_INTERVAL) {
      previousMillis = currentMillis; // Reset timer
      digitalWrite(BUZZER_PIN, HIGH); // Turn on the buzzer
      delay(1000); // Keep the buzzer on for 1 second
      digitalWrite(BUZZER_PIN, LOW); // Turn off the buzzer
    }
  }

  delay(50); // Short delay for stability
}
