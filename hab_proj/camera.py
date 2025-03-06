"""
Módulo para gerenciar a câmera e integrar com o modelo de IA.
"""

import cv2
import numpy as np
import time

class Camera:
    """Classe para gerenciar a câmera e integrar com o modelo de IA."""
    
    def __init__(self, camera_id=0, model=None):
        """
        Inicializa a câmera.
        
        Args:
            camera_id (int): ID da câmera (0 geralmente é a webcam integrada)
            model (AIModel, optional): Instância do modelo de IA
        """
        self.camera_id = camera_id
        self.model = model
        self.cap = None
        
    def start(self):
        """Inicia a câmera."""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError("Erro: Não foi possível acessar a câmera.")
            
        print(f"Câmera {self.camera_id} iniciada. Pressione 'q' para sair.")
        return self.cap.isOpened()
    
    def stop(self):
        """Libera os recursos da câmera."""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            print("Câmera desligada.")
    
    def read_frame(self):
        """
        Lê um frame da câmera.
        
        Returns:
            numpy.ndarray or None: Frame capturado ou None se houver erro
        """
        if self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            print("Erro: Não foi possível ler o frame.")
            return None
            
        return frame
    
    def run_with_model(self, display_fps=True, prediction_interval=0.5):
        """
        Executa a câmera com o modelo de IA para classificação em tempo real.
        
        Args:
            display_fps (bool): Se deve exibir o FPS na tela
            prediction_interval (float): Intervalo em segundos entre predições
        """
        if self.model is None:
            raise ValueError("Modelo de IA não fornecido.")
            
        if not self.start():
            return
            
        last_prediction_time = 0
        fps_start_time = 0
        frame_count = 0
        fps = 0
        current_prediction = "Aguardando..."
        current_confidence = 0.0
        
        try:
            while True:
                frame = self.read_frame()
                if frame is None:
                    break
                    
                # Calcular FPS
                if display_fps:
                    current_time = time.time()
                    frame_count += 1
                    
                    if current_time - fps_start_time >= 1.0:
                        fps = frame_count / (current_time - fps_start_time)
                        fps_start_time = current_time
                        frame_count = 0
                
                # Fazer predição em intervalos regulares
                if time.time() - last_prediction_time >= prediction_interval:
                    if self.model is not None:
                        current_prediction, current_confidence, _ = self.model.predict(frame)
                        last_prediction_time = time.time()
                
                # Exibir informações na tela
                self._display_info(frame, current_prediction, current_confidence, fps if display_fps else None)
                
                # Exibir o frame
                cv2.imshow('Câmera com IA', frame)
                
                # Verificar se a tecla 'q' foi pressionada para sair
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            self.stop()
    
    def _display_info(self, frame, prediction, confidence, fps=None):
        """
        Exibe informações na tela.
        
        Args:
            frame (numpy.ndarray): Frame atual
            prediction (str): Predição atual
            confidence (float): Confiança da predição
            fps (float, optional): FPS atual
        """
        # Configurações de texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        text_color = (255, 255, 255)  # Branco
        bg_color = (0, 0, 0)  # Preto
        
        # Adicionar informações de predição
        prediction_text = f"Predição: {prediction}"
        confidence_text = f"Confiança: {confidence:.2f}"
        
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