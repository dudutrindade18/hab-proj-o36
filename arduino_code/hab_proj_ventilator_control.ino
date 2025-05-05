/*
 * HAB Project - Ventilator Control
 * 
 * This code combines the HAB Project receiver functionality with ventilator/dimmer control:
 * - '0': Turns OFF the ventilator
 * - '1': Turns ON the ventilator at the last set intensity
 * - '2': Set LOW intensity (firing delay = 6000)
 * - '3': Set MEDIUM intensity (firing delay = 4000)
 * - '4': Set MAXIMUM intensity (firing delay = 2000)
 * - 'ping': Command to verify if Arduino is connected
 * 
 * Hardware:
 * - Zero-crossing detector connected to pin 3
 * - TRIAC control connected to pin 2
 * - Arduino connected to computer via USB
 */

// Zero-crossing detection
volatile boolean zeroCrossDetected = false;
int currentFiringDelay = 6000; // Initial delay set to low (6000 = low power, 0 = max power)
int firingDelay = 8000;        // Actual firing delay (8000 = off, currentFiringDelay = on)
boolean isOn = false;          // Current state of the ventilator

// Pins
const int TRIAC_PIN = 2;        // Pin connected to TRIAC gate
const int ZC_INTERRUPT_PIN = 3; // Pin connected to zero-crossing detector
const int LED_PIN = LED_BUILTIN; // LED for visual feedback

// Safety settings
unsigned long lastZeroCrossTime = 0;
const unsigned long TIMEOUT = 1000; // 1 second timeout

void setup() {
  // Pin configuration
  pinMode(TRIAC_PIN, OUTPUT);
  digitalWrite(TRIAC_PIN, LOW);
  pinMode(ZC_INTERRUPT_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Zero-crossing interrupt setup
  attachInterrupt(digitalPinToInterrupt(ZC_INTERRUPT_PIN), zeroCrossISR, RISING);
  
  // Serial communication initialization
  Serial.begin(9600);
  
  // Visual startup signal
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
  
  Serial.println("Arduino ready to receive commands!");
  Serial.println("Commands: '0' = OFF, '1' = ON, '2' = LOW intensity, '3' = MEDIUM intensity, '4' = MAXIMUM intensity");
}

void loop() {
  // Process serial commands
  processSerialCommands();
  
  // Update actual firing delay based on state
  firingDelay = isOn ? currentFiringDelay : 8000; // 8000 = OFF
  
  // TRIAC control based on zero-crossing detection
  if (zeroCrossDetected) {
    delayMicroseconds(firingDelay);
    digitalWrite(TRIAC_PIN, HIGH);
    delayMicroseconds(10); // short pulse to gate
    digitalWrite(TRIAC_PIN, LOW);
    zeroCrossDetected = false;
    lastZeroCrossTime = millis();
  }
  
  // Safety check - if no zero-crossing pulses for a certain time, turn off
  if (isOn && (millis() - lastZeroCrossTime > TIMEOUT)) {
    isOn = false;
    Serial.println("Safety timeout: No zero-crossing detected. Turning OFF.");
    digitalWrite(LED_PIN, LOW);
  }
}

// Interrupt function for zero-crossing detection
void zeroCrossISR() {
  zeroCrossDetected = true;
}

// Function to process commands received via serial
void processSerialCommands() {
  if (Serial.available() > 0) {
    // Read the complete string until newline
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove spaces and newline characters
    
    // Check ping command
    if (input == "ping") {
      Serial.println("Arduino ready to receive commands!");
    }
    // Command to turn ON with current intensity
    else if (input == "1") {
      isOn = true;
      lastZeroCrossTime = millis(); // Reset safety timer
      digitalWrite(LED_PIN, HIGH);  // Turn on LED for visual feedback
      
      // Report current intensity
      String intensity;
      if (currentFiringDelay >= 6000) intensity = "LOW";
      else if (currentFiringDelay >= 4000) intensity = "MEDIUM";
      else intensity = "MAXIMUM";
      
      Serial.println("Ventilator ON: " + intensity + " intensity");
    }
    // Command to turn OFF
    else if (input == "0") {
      isOn = false;
      digitalWrite(LED_PIN, LOW);  // Turn off LED
      Serial.println("Ventilator OFF");
    }
    // Command to set LOW intensity
    else if (input == "2") {
      currentFiringDelay = 6000;
      Serial.println("Intensity set to LOW");
      
      // Update status message if already on
      if (isOn) {
        Serial.println("Ventilator ON: LOW intensity");
      }
    }
    // Command to set MEDIUM intensity
    else if (input == "3") {
      currentFiringDelay = 4000;
      Serial.println("Intensity set to MEDIUM");
      
      // Update status message if already on
      if (isOn) {
        Serial.println("Ventilator ON: MEDIUM intensity");
      }
    }
    // Command to set MAXIMUM intensity
    else if (input == "4") {
      currentFiringDelay = 2000;
      Serial.println("Intensity set to MAXIMUM");
      
      // Update status message if already on
      if (isOn) {
        Serial.println("Ventilator ON: MAXIMUM intensity");
      }
    }
  }
} 