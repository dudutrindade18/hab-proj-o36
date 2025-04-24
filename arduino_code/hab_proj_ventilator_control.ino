/*
 * HAB Project - Ventilator Control
 * 
 * This code combines the HAB Project receiver functionality with ventilator/dimmer control:
 * - '1': Turns ON the ventilator at high power
 * - '0': Turns OFF the ventilator
 * - '2': Medium power (optional)
 * - '3': Low power (optional)
 * - 'ping': Command to verify if Arduino is connected
 * 
 * Hardware:
 * - Zero-crossing detector connected to pin 3
 * - TRIAC control connected to pin 2
 * - Arduino connected to computer via USB
 */

// Zero-crossing detection
volatile boolean zeroCrossDetected = false;
int firingDelay = 8000; // em microssegundos (8000 = desligado, 0 = potência máxima)
boolean isOn = false;   // Estado atual do ventilador

// Pinos
const int TRIAC_PIN = 2;        // Pino conectado ao gate do TRIAC
const int ZC_INTERRUPT_PIN = 3; // Pino conectado ao detector de zero-crossing
const int LED_PIN = LED_BUILTIN; // LED para feedback visual

// Configurações de segurança
unsigned long lastZeroCrossTime = 0;
const unsigned long TIMEOUT = 1000; // 1 segundo de timeout

void setup() {
  // Configuração dos pinos
  pinMode(TRIAC_PIN, OUTPUT);
  digitalWrite(TRIAC_PIN, LOW);
  pinMode(ZC_INTERRUPT_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Configuração da interrupção de zero-crossing
  attachInterrupt(digitalPinToInterrupt(ZC_INTERRUPT_PIN), zeroCrossISR, RISING);
  
  // Inicialização da comunicação serial
  Serial.begin(9600);
  
  // Sinalização visual de inicialização
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
  
  Serial.println("Arduino ready to receive commands!");
  Serial.println("Commands: '0' = OFF, '1' = HIGH power, '2' = MEDIUM power, '3' = LOW power");
}

void loop() {
  // Processamento de comandos seriais
  processSerialCommands();
  
  // Controle do TRIAC baseado na detecção de zero-crossing
  if (zeroCrossDetected && isOn) {
    delayMicroseconds(firingDelay);
    digitalWrite(TRIAC_PIN, HIGH);
    delayMicroseconds(10); // pulso curto no gate
    digitalWrite(TRIAC_PIN, LOW);
    zeroCrossDetected = false;
    lastZeroCrossTime = millis();
  }
  
  // Verificação de segurança - se não houver pulsos de zero-crossing por um certo tempo, desliga
  if (isOn && (millis() - lastZeroCrossTime > TIMEOUT)) {
    isOn = false;
    Serial.println("Safety timeout: No zero-crossing detected. Turning OFF.");
    digitalWrite(LED_PIN, LOW);
  }
}

// Função de interrupção para detecção de zero-crossing
void zeroCrossISR() {
  zeroCrossDetected = true;
}

// Função para processar comandos recebidos via serial
void processSerialCommands() {
  if (Serial.available() > 0) {
    // Ler a string completa até encontrar newline
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remover espaços e caracteres de newline
    
    // Verificar comando ping
    if (input == "ping") {
      Serial.println("Arduino ready to receive commands!");
    }
    // Comando para ligar em potência máxima
    else if (input == "1") {
      // Liga na potência máxima
      firingDelay = 0;
      isOn = true;
      lastZeroCrossTime = millis(); // Reset do timer de segurança
      digitalWrite(LED_PIN, HIGH);  // Liga o LED para feedback visual
      Serial.println("Ventilator ON: HIGH power");
    }
    // Comando para ligar em potência média
    else if (input == "2") {
      // Liga na potência média
      firingDelay = 3000;
      isOn = true;
      lastZeroCrossTime = millis(); // Reset do timer de segurança
      digitalWrite(LED_PIN, HIGH);  // Liga o LED para feedback visual
      Serial.println("Ventilator ON: MEDIUM power");
    }
    // Comando para ligar em potência baixa
    else if (input == "3") {
      // Liga na potência baixa
      firingDelay = 6000;
      isOn = true;
      lastZeroCrossTime = millis(); // Reset do timer de segurança
      digitalWrite(LED_PIN, HIGH);  // Liga o LED para feedback visual
      Serial.println("Ventilator ON: LOW power");
    }
    // Comando para desligar
    else if (input == "0") {
      // Desliga o ventilador
      isOn = false;
      digitalWrite(LED_PIN, LOW);  // Desliga o LED
      Serial.println("Ventilator OFF");
    }
  }
} 