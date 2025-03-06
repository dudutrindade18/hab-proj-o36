"""
Módulo para carregar e utilizar o modelo de IA para classificação.
"""

import os
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2

class AIModel:
    """Classe para gerenciar o modelo de IA para classificação."""
    
    def __init__(self, model_path, labels_path):
        """
        Inicializa o modelo de IA.
        
        Args:
            model_path (str): Caminho para o arquivo do modelo (.h5)
            labels_path (str): Caminho para o arquivo de labels (.txt)
        """
        self.model = tf.keras.models.load_model(model_path)
        self.labels = self._load_labels(labels_path)
        
        # Obtém as dimensões de entrada esperadas pelo modelo
        self.input_shape = self.model.input_shape[1:3]  # (altura, largura)
        
    def _load_labels(self, labels_path):
        """
        Carrega as labels do modelo a partir de um arquivo de texto.
        
        Args:
            labels_path (str): Caminho para o arquivo de labels
            
        Returns:
            dict: Dicionário mapeando índices para nomes de classes
        """
        labels = {}
        with open(labels_path, 'r') as file:
            for line in file:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    index, label = parts
                    labels[int(index)] = label
        return labels
    
    def preprocess_image(self, image):
        """
        Pré-processa a imagem para o formato esperado pelo modelo.
        
        Args:
            image: Imagem OpenCV (BGR)
            
        Returns:
            np.array: Imagem pré-processada
        """
        # Converter BGR para RGB (OpenCV usa BGR, TensorFlow espera RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Redimensionar para o tamanho esperado pelo modelo
        pil_image = Image.fromarray(image_rgb)
        resized_image = pil_image.resize(self.input_shape)
        
        # Normalizar os valores dos pixels para [0, 1]
        img_array = np.array(resized_image) / 255.0
        
        # Adicionar dimensão de batch
        return np.expand_dims(img_array, axis=0)
    
    def predict(self, image):
        """
        Realiza a predição em uma imagem.
        
        Args:
            image: Imagem OpenCV (BGR)
            
        Returns:
            tuple: (classe_predita, confiança, todas_as_probabilidades)
        """
        # Pré-processar a imagem
        processed_image = self.preprocess_image(image)
        
        # Fazer a predição
        predictions = self.model.predict(processed_image)[0]
        
        # Obter a classe com maior probabilidade
        predicted_class_index = np.argmax(predictions)
        confidence = predictions[predicted_class_index]
        
        # Obter o nome da classe
        class_name = self.labels.get(predicted_class_index, f"Classe {predicted_class_index}")
        
        return class_name, confidence, predictions 