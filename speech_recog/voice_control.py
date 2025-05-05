import os
import sys
import threading
import time
import pyaudio
import json

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from speech_recog.voice_recognition import VoiceRecognizer

class VoiceControl:
    def __init__(self, callback=None):
        self.recognizer = VoiceRecognizer()
        self.callback = callback
        self.running = False
        self.thread = None
        
        # Mapeamento de comandos para valores
        self.command_values = {
            "low": 2,
            "medium": 3,
            "maximum": 4
        }

    def start(self):
        """Inicia o reconhecimento de voz em uma thread separada"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_recognition)
            self.thread.daemon = True
            self.thread.start()
            print("Reconhecimento de voz iniciado")
            print("Diga: 'low', 'medium' ou 'maximum'...")

    def stop(self):
        """Para o reconhecimento de voz"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            self.recognizer.stop_recognition()
            print("Reconhecimento de voz parado")

    def set_command_callback(self, callback):
        """Define a função de callback para comandos de voz"""
        self.callback = callback

    def _run_recognition(self):
        """Loop principal de reconhecimento de voz"""
        self.recognizer.start_recognition()
        
        while self.running:
            command = self.recognizer.get_command()
            if command:
                value = self.command_values.get(command.lower())
                if value is not None:
                    print(f"Comando reconhecido: {command.upper()} (valor: {value})")
                    if self.callback:
                        self.callback(command, value)
                else:
                    print(f"Comando não reconhecido: {command}")

    def __del__(self):
        """Garante que o reconhecimento seja parado ao destruir o objeto"""
        self.stop()

# Exemplo de uso
if __name__ == "__main__":
    def on_voice_command(command, value):
        print(f"Função de callback chamada com comando: {command}, valor: {value}")
    
    # Cria e inicia o controle de voz
    voice_control = VoiceControl(callback=on_voice_command)
    voice_control.start()
    
    try:
        # Mantém o programa principal em execução
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nEncerrando o programa...")
    finally:
        voice_control.stop() 