"""
Module for loading and using the AI model for classification.
"""

import os
import numpy as np
import cv2
from PIL import Image

# Try to import TensorFlow, fall back to TensorFlow Lite if not available
try:
    import tensorflow as tf
    USE_TFLITE = False
    print("Using TensorFlow")
except ImportError:
    try:
        import tflite_runtime.interpreter as tflite
        USE_TFLITE = True
        print("Using TensorFlow Lite")
    except ImportError:
        raise ImportError("Neither TensorFlow nor TensorFlow Lite is available. Please install one of them.")

class AIModel:
    """Class to manage the AI model for classification."""
    
    def __init__(self, model_path, labels_path):
        """
        Initialize the AI model.
        
        Args:
            model_path (str): Path to the model file (.h5 or .tflite)
            labels_path (str): Path to the labels file (.txt)
        """
        # Load the model based on the available framework and file extension
        if model_path.endswith('.tflite') or USE_TFLITE:
            # If the model is a .h5 file but we're using TFLite, try to find a .tflite version
            if model_path.endswith('.h5') and USE_TFLITE:
                tflite_path = model_path.replace('.h5', '.tflite')
                if os.path.exists(tflite_path):
                    model_path = tflite_path
                else:
                    raise ValueError(f"TensorFlow Lite is being used, but no .tflite model found at {tflite_path}")
            
            # Load TFLite model
            self._load_tflite_model(model_path)
        else:
            # Load Keras model
            self._load_keras_model(model_path)
            
        # Load labels
        self.labels = self._load_labels(labels_path)
    
    def _load_keras_model(self, model_path):
        """Load a Keras model."""
        self.model = tf.keras.models.load_model(model_path)
        self.input_shape = self.model.input_shape[1:3]  # (height, width)
        self.use_tflite = False
    
    def _load_tflite_model(self, model_path):
        """Load a TFLite model."""
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Get input shape
        self.input_shape = self.input_details[0]['shape'][1:3]  # (height, width)
        self.use_tflite = True
    
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
        img_array = np.expand_dims(img_array, axis=0)
        
        # Convert to float32 for TFLite
        img_array = img_array.astype(np.float32)
        
        return img_array
    
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
        
        # Make prediction based on the model type
        if hasattr(self, 'use_tflite') and self.use_tflite:
            # TFLite prediction
            self.interpreter.set_tensor(self.input_details[0]['index'], processed_image)
            self.interpreter.invoke()
            predictions = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        else:
            # Keras prediction
            predictions = self.model.predict(processed_image)[0]
        
        # Get the class with the highest probability
        predicted_class_index = np.argmax(predictions)
        confidence = predictions[predicted_class_index]
        
        # Get the class name
        class_name = self.labels.get(predicted_class_index, f"Class {predicted_class_index}")
        
        return class_name, confidence, predictions 