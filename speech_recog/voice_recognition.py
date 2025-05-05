from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
import sys

class VoiceRecognizer:
    def __init__(self, model_path=None):
        """
        Inicializa o reconhecimento de voz usando o modelo Vosk
        
        Args:
            model_path: Caminho para o modelo Vosk (opcional)
        """
        if model_path is None:
            # Usa o caminho padrão do modelo
            model_path = os.path.join(os.path.dirname(__file__), "model-en-us-small")
            
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo Vosk não encontrado em {model_path}")
            
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        
        # Comandos reconhecidos
        self.commands = ["low", "medium", "maximum"]
        
    def start_recognition(self):
        """Inicia o reconhecimento de voz"""
        if self.stream is not None:
            return
            
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096
        )
        self.stream.start_stream()
        self.running = True
        
    def stop_recognition(self):
        """Para o reconhecimento de voz"""
        if self.stream is not None:
            self.running = False
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
    def get_command(self):
        """
        Obtém o próximo comando de voz reconhecido
        
        Returns:
            str: O comando reconhecido ou None se nenhum comando foi reconhecido
        """
        if not self.running or self.stream is None:
            return None
            
        data = self.stream.read(4096, exception_on_overflow=False)
        
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").lower()
            
            if text:
                # Verifica se alguma das palavras-chave foi reconhecida
                for command in self.commands:
                    if command in text:
                        return command
                        
        return None
        
    def __del__(self):
        """Garante que os recursos sejam liberados ao destruir o objeto"""
        self.stop_recognition()
        self.audio.terminate()

if __name__ == "__main__":
    recognizer = VoiceRecognizer()
    recognizer.start_recognition() 