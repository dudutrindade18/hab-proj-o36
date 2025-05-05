from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
import sys

class VoiceRecognizer:
    def __init__(self, model_path=None):
        """
        Inicializa o reconhecedor de voz com modelo Vosk
        
        Args:
            model_path: Caminho para o modelo Vosk (se None, usará 'model-en-us-small')
        """
        # Se não for fornecido um caminho de modelo, usamos o diretório padrão
        if model_path is None:
            # Obtém o diretório do script atual
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, "model-en-us-small")
        
        # Verifica se o modelo existe
        if not os.path.exists(model_path):
            print(f"Modelo não encontrado em: {model_path}")
            print("Por favor, baixe o modelo usando o script download_model.py primeiro.")
            sys.exit(1)
            
        # Inicializa o modelo Vosk
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        
        # Inicializa o PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Flag para controlar o loop de reconhecimento
        self.running = False
        
        # Última palavra reconhecida
        self.last_recognized = None
        
    def start(self):
        """Inicia a captura de áudio e o reconhecimento"""
        # Configura e inicia o stream de áudio
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096
        )
        self.stream.start_stream()
        self.running = True
        
        print("Reconhecimento de voz iniciado.")
        print("Diga: 'low', 'medium' ou 'maximum'...")
        
        try:
            while self.running:
                data = self.stream.read(4096, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower()
                    
                    if text:
                        print(f"Você disse: {text}")
                        
                        # Verifica se alguma das palavras-chave foi reconhecida
                        if "low" in text:
                            print("Comando reconhecido: LOW (30%)")
                            self.last_recognized = "low"
                        elif "medium" in text:
                            print("Comando reconhecido: MEDIUM (60%)")
                            self.last_recognized = "medium"
                        elif "maximum" in text:
                            print("Comando reconhecido: MAXIMUM (100%)")
                            self.last_recognized = "maximum"
                
        except KeyboardInterrupt:
            print("\nReconhecimento de voz interrompido pelo usuário.")
        finally:
            self.stop()
    
    def stop(self):
        """Para a captura de áudio e libera recursos"""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        if self.audio:
            self.audio.terminate()
            
        print("Reconhecimento de voz finalizado.")

if __name__ == "__main__":
    recognizer = VoiceRecognizer()
    recognizer.start() 