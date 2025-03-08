/*
 * HAB Project - Arduino Receiver
 * 
 * This code receives commands from the Python application via serial port:
 * - '1': Turns ON the LED (when classification is "Good")
 * - '0': Turns OFF the LED (when classification is "Bad")
 * - 'ping': Command to verify if Arduino is connected
 * 
 * Connection:
 * - Connect Arduino to computer via USB
 * - Run the Python application
 */

void setup() {
  Serial.begin(9600);              // Initialize serial communication with the same baud rate
  pinMode(LED_BUILTIN, OUTPUT);    // Configure built-in LED as output
  
  // Blink LED to indicate Arduino is ready
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
  
  Serial.println("Arduino ready to receive commands!");
}

void loop() {
  if (Serial.available() > 0) {          // Check if data is available
    // Read the complete string until newline
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove whitespace and newline characters
    
    // Check if it's a ping command
    if (input == "ping") {
      Serial.println("Arduino ready to receive commands!");
    }
    // Check if it's the command to turn ON the LED
    else if (input == "1") {
      digitalWrite(LED_BUILTIN, HIGH);   // Turn ON LED if '1' is received
      Serial.println("LED ON");          // Send confirmation
    } 
    // Check if it's the command to turn OFF the LED
    else if (input == "0") {
      digitalWrite(LED_BUILTIN, LOW);    // Turn OFF LED if '0' is received
      Serial.println("LED OFF");         // Send confirmation
    }
  }
}
