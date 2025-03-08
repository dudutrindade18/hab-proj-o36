"""
Module for loading and using the AI model for classification.
"""

import os
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2

class AIModel:
    """Class to manage the AI model for classification."""
    
    def __init__(self, model_path, labels_path):
        """
        Initialize the AI model.
        
        Args:
            model_path (str): Path to the model file (.h5)
            labels_path (str): Path to the labels file (.txt)
        """
        self.model = tf.keras.models.load_model(model_path)
        self.labels = self._load_labels(labels_path)
        
        # Get the expected input dimensions for the model
        self.input_shape = self.model.input_shape[1:3]  # (height, width)
        
    def _load_labels(self, labels_path):
        """
        Load model labels from a text file.
        
        Args:
            labels_path (str): Path to the labels file
            
        Returns:
            dict: Dictionary mapping indices to class names
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
        Preprocess the image to the format expected by the model.
        
        Args:
            image: OpenCV image (BGR)
            
        Returns:
            np.array: Preprocessed image
        """
        # Convert BGR to RGB (OpenCV uses BGR, TensorFlow expects RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to the expected size for the model
        pil_image = Image.fromarray(image_rgb)
        resized_image = pil_image.resize(self.input_shape)
        
        # Normalize pixel values to [0, 1]
        img_array = np.array(resized_image) / 255.0
        
        # Add batch dimension
        return np.expand_dims(img_array, axis=0)
    
    def predict(self, image):
        """
        Make a prediction on an image.
        
        Args:
            image: OpenCV image (BGR)
            
        Returns:
            tuple: (predicted_class, confidence, all_probabilities)
        """
        # Preprocess the image
        processed_image = self.preprocess_image(image)
        
        # Make the prediction
        predictions = self.model.predict(processed_image)[0]
        
        # Get the class with the highest probability
        predicted_class_index = np.argmax(predictions)
        confidence = predictions[predicted_class_index]
        
        # Get the class name
        class_name = self.labels.get(predicted_class_index, f"Class {predicted_class_index}")
        
        return class_name, confidence, predictions 