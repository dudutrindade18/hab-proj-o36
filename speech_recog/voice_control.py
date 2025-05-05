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

class VoiceControlThread:
    def __init__(self, model_path=None, callback=None):
        """
        Inicializa o controle de voz em uma thread separada
        
        Args:
            model_path: Caminho para o modelo Vosk
            callback: Função de callback a ser chamada quando um comando for reconhecido
                      Formato: callback(command, value)
                      Onde command é a string e value é o valor associado (0-100)
        """
        self.recognizer = VoiceRecognizer(model_path)
        self.callback = callback
        self.thread = None
        self.running = False
        
        # Mapeamento de comandos para valores
        self.command_values = {
            "low": 30,
            "medium": 60,
            "maximum": 100
        }
    
    def _run(self):
        """Função que executa na thread"""
        self.recognizer.running = True
        
        # Configura e inicia o stream de áudio
        self.recognizer.stream = self.recognizer.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096
        )
        self.recognizer.stream.start_stream()
        
        print("Reconhecimento de voz iniciado.")
        print("Diga: 'low', 'medium' ou 'maximum'...")
        
        try:
            while self.running and self.recognizer.running:
                data = self.recognizer.stream.read(4096, exception_on_overflow=False)
                
                if self.recognizer.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.recognizer.Result())
                    text = result.get("text", "").lower()
                    
                    if text:
                        print(f"Você disse: {text}")
                        
                        command = None
                        value = 0
                        
                        # Verifica se alguma das palavras-chave foi reconhecida
                        if "low" in text:
                            command = "low"
                            value = self.command_values[command]
                            print(f"Comando reconhecido: LOW ({value}%)")
                        elif "medium" in text:
                            command = "medium"
                            value = self.command_values[command]
                            print(f"Comando reconhecido: MEDIUM ({value}%)")
                        elif "maximum" in text:
                            command = "maximum"
                            value = self.command_values[command]
                            print(f"Comando reconhecido: MAXIMUM ({value}%)")
                        
                        # Se um comando foi reconhecido e existe um callback, chama o callback
                        if command and self.callback:
                            self.callback(command, value)
                
                # Pequena pausa para não sobrecarregar a CPU
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Erro no reconhecimento de voz: {e}")
        finally:
            self.recognizer.stop()
    
    def start(self):
        """Inicia a thread de reconhecimento de voz"""
        if self.thread and self.thread.is_alive():
            print("A thread de reconhecimento de voz já está em execução.")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True  # Thread vai terminar quando o programa principal terminar
        self.thread.start()
        
        return self.thread
    
    def stop(self):
        """Para a thread de reconhecimento de voz"""
        self.running = False
        self.recognizer.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)  # Espera a thread terminar com timeout
            
# Exemplo de uso
if __name__ == "__main__":
    def on_voice_command(command, value):
        print(f"Função de callback chamada com comando: {command}, valor: {value}")
    
    # Cria e inicia o controle de voz
    voice_control = VoiceControlThread(callback=on_voice_command)
    voice_control.start()
    
    try:
        # Mantém o programa principal em execução
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nEncerrando o programa...")
    finally:
        voice_control.stop() 