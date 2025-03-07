/*
 * HAB Project - Receptor Arduino
 * 
 * Este código recebe comandos da aplicação Python via porta serial:
 * - '1': Liga o LED (quando a classificação é "Bom")
 * - '0': Desliga o LED (quando a classificação é "Ruim")
 * 
 * Conexão:
 * - Conecte o Arduino ao computador via USB
 * - Execute a aplicação Python com a opção --arduino
 */

void setup() {
  Serial.begin(9600);  // Iniciar comunicação serial com a mesma taxa de transmissão (baud rate)
  pinMode(LED_BUILTIN, OUTPUT);  // Configurar LED embutido como saída
  
  // Piscar o LED para indicar que o Arduino está pronto
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
}

void loop() {
  if (Serial.available() > 0) {  // Verificar se há dados disponíveis
    char command = Serial.read();  // Ler um byte
    
    if (command == '1') {
      digitalWrite(LED_BUILTIN, HIGH);  // Ligar LED se receber '1'
      Serial.println("LED ON");  // Enviar confirmação
    } 
    else if (command == '0') {
      digitalWrite(LED_BUILTIN, LOW);   // Desligar LED se receber '0'
      Serial.println("LED OFF");  // Enviar confirmação
    }
  }
} 