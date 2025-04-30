import os
import sys
# Adicionar o diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

import threading
import time
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import cv2
import numpy as np
from hab_proj.model import AIModel

class IntegratedSystem:
    def __init__(self, camera_id=0):
        # Obter caminhos absolutos para os modelos
        voice_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model-pt")
        vision_model_path = os.path.join(root_dir, 'converted_keras', 'keras_model.h5')
        vision_labels_path = os.path.join(root_dir, 'converted_keras', 'labels.txt')
        
        # Verificar se os arquivos existem
        if not os.path.exists(vision_model_path):
            raise FileNotFoundError(f"Modelo de visão não encontrado em: {vision_model_path}")
        if not os.path.exists(vision_labels_path):
            raise FileNotFoundError(f"Arquivo de labels não encontrado em: {vision_labels_path}")
        
        # Inicializar o modelo de voz
        self.voice_model = Model(voice_model_path)
        self.voice_rec = KaldiRecognizer(self.voice_model, 16000)
        
        # Inicializar o modelo de visão
        self.vision_model = AIModel(vision_model_path, vision_labels_path)
        
        # Inicializar a câmera
        self.camera_id = camera_id
        self.cap = None
        
        # Inicializar o áudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                                input=True, frames_per_buffer=4096)
        
        # Flags de controle
        self.running = True
        self.voice_thread = None
        self.vision_thread = None
        
    def voice_recognition(self):
        """Thread para reconhecimento de voz"""
        print("Diga: fraco, medio ou forte...")
        self.stream.start_stream()
        
        try:
            while self.running:
                data = self.stream.read(4096)
                if self.voice_rec.AcceptWaveform(data):
                    result = json.loads(self.voice_rec.Result())
                    texto = result["text"]
                    print("Você disse:", texto)
                    
                    if "fraco" in texto:
                        print("Modo: FRACO (30%)")
                    elif "médio" in texto:
                        print("Modo: MÉDIO (60%)")
                    elif "forte" in texto:
                        print("Modo: FORTE (100%)")
        except Exception as e:
            print(f"Erro no reconhecimento de voz: {e}")
        finally:
            self.stream.stop_stream()
            
    def display_info(self, frame, prediction, confidence, fps=None):
        """Mostrar informações na tela"""
        # Configurações do texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        text_color = (255, 255, 255)  # Branco
        bg_color = (0, 0, 0)  # Preto
        
        # Adicionar informações de previsão
        prediction_text = f"Prediction: {prediction}"
        confidence_text = f"Confidence: {confidence:.2f}"
        
        # Posição do texto
        y_pos = 30
        
        # Função para adicionar texto com fundo
        def add_text_with_background(text, y):
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            cv2.rectangle(frame, (10, y - 25), (10 + text_size[0], y + 5), bg_color, -1)
            cv2.putText(frame, text, (10, y), font, font_scale, text_color, font_thickness)
            return y + 40
        
        # Adicionar textos
        y_pos = add_text_with_background(prediction_text, y_pos)
        y_pos = add_text_with_background(confidence_text, y_pos)
        
        # Adicionar FPS se disponível
        if fps is not None:
            fps_text = f"FPS: {fps:.1f}"
            add_text_with_background(fps_text, y_pos)
            
    def vision_recognition(self):
        """Thread para reconhecimento de visão"""
        try:
            # Inicializar a câmera
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print("Erro: Não foi possível abrir a câmera")
                return
                
            print("Câmera iniciada. Pressione 'q' para sair.")
            
            last_prediction_time = 0
            fps_start_time = time.time()
            frame_count = 0
            fps = 0
            current_prediction = "Waiting..."
            current_confidence = 0.0
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Erro: Não foi possível ler o frame da câmera")
                    break
                    
                # Calcular FPS
                current_time = time.time()
                frame_count += 1
                
                if current_time - fps_start_time >= 1.0:
                    fps = frame_count / (current_time - fps_start_time)
                    fps_start_time = current_time
                    frame_count = 0
                
                # Fazer previsão em intervalos regulares
                if time.time() - last_prediction_time >= 0.5:  # 0.5 segundos entre previsões
                    current_prediction, current_confidence, _ = self.vision_model.predict(frame)
                    last_prediction_time = time.time()
                
                # Mostrar informações na tela
                self.display_info(frame, current_prediction, current_confidence, fps)
                
                # Mostrar o frame
                cv2.imshow('Camera with AI', frame)
                
                # Verificar se a tecla 'q' foi pressionada
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            print(f"Erro no reconhecimento de visão: {e}")
        finally:
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            
    def start(self):
        """Iniciar o sistema integrado"""
        # Iniciar threads
        self.voice_thread = threading.Thread(target=self.voice_recognition)
        self.vision_thread = threading.Thread(target=self.vision_recognition)
        
        self.voice_thread.start()
        self.vision_thread.start()
        
        try:
            # Manter o programa rodando
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nEncerrando o sistema...")
            self.stop()
            
    def stop(self):
        """Parar o sistema integrado"""
        self.running = False
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
        if self.voice_thread:
            self.voice_thread.join()
        if self.vision_thread:
            self.vision_thread.join()

if __name__ == "__main__":
    system = IntegratedSystem()
    system.start() 