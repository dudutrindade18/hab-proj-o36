"""
Module for managing the camera and integrating with the AI model.
"""

import cv2
import numpy as np
import time
import os

class Camera:
    """Class for managing the camera and integrating with the AI model."""
    
    def __init__(self, camera_id=0, model=None, arduino_serial=None):
        """
        Initialize the camera.
        
        Args:
            camera_id (int): Camera ID (0 is usually the built-in webcam)
            model (AIModel, optional): AI model instance
            arduino_serial (ArduinoSerial, optional): Arduino serial communication instance
        """
        self.camera_id = camera_id
        self.model = model
        self.arduino_serial = arduino_serial
        self.cap = None
        self.width = 640
        self.height = 480
        
    def start(self):
        """Start the camera."""
        # Try different camera backends if the default doesn't work
        # This is especially useful on Raspberry Pi
        backends = [cv2.CAP_ANY]
        
        # On Raspberry Pi, try specific backends
        if os.path.exists('/proc/device-tree/model') and 'raspberry pi' in open('/proc/device-tree/model').read().lower():
            backends.extend([
                cv2.CAP_V4L,       # Video for Linux
                cv2.CAP_V4L2,      # Video for Linux 2
                cv2.CAP_GSTREAMER  # GStreamer
            ])
        
        # Try each backend until one works
        for backend in backends:
            try:
                self.cap = cv2.VideoCapture(self.camera_id, backend)
                if self.cap.isOpened():
                    break
            except Exception as e:
                print(f"Backend {backend} failed: {e}")
        
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError("Error: Could not access the camera.")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Get actual resolution (may be different from requested)
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera {self.camera_id} started with resolution: {actual_width}x{actual_height}")
        print("Press 'q' to quit.")
        
        return self.cap.isOpened()
    
    def stop(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            print("Camera turned off.")
    
    def read_frame(self):
        """
        Read a frame from the camera.
        
        Returns:
            numpy.ndarray or None: Captured frame or None if there's an error
        """
        if self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Could not read frame.")
            return None
            
        return frame
    
    def run_with_model(self, display_fps=True, prediction_interval=0.5, headless=False):
        """
        Run the camera with the AI model for real-time classification.
        
        Args:
            display_fps (bool): Whether to display FPS on screen
            prediction_interval (float): Interval in seconds between predictions
            headless (bool): Whether to run in headless mode (no GUI)
        """
        if self.model is None:
            raise ValueError("AI model not provided.")
            
        if not self.start():
            return
            
        last_prediction_time = 0
        fps_start_time = 0
        frame_count = 0
        fps = 0
        current_prediction = "Waiting..."
        current_confidence = 0.0
        
        # Connect to Arduino if available
        if self.arduino_serial:
            self.arduino_serial.connect()
        
        try:
            while True:
                frame = self.read_frame()
                if frame is None:
                    break
                    
                # Calculate FPS
                if display_fps:
                    current_time = time.time()
                    frame_count += 1
                    
                    if current_time - fps_start_time >= 1.0:
                        fps = frame_count / (current_time - fps_start_time)
                        fps_start_time = current_time
                        frame_count = 0
                
                # Make prediction at regular intervals
                if time.time() - last_prediction_time >= prediction_interval:
                    if self.model is not None:
                        current_prediction, current_confidence, _ = self.model.predict(frame)
                        last_prediction_time = time.time()
                        
                        # Send command to Arduino based on prediction
                        if self.arduino_serial:
                            self.arduino_serial.send_label_command(current_prediction)
                        
                        # Print prediction in headless mode
                        if headless:
                            print(f"Prediction: {current_prediction}, Confidence: {current_confidence:.2f}")
                
                # Display information on screen if not in headless mode
                if not headless:
                    self._display_info(frame, current_prediction, current_confidence, fps if display_fps else None)
                    
                    # Display the frame
                    cv2.imshow('Camera with AI', frame)
                    
                    # Check if 'q' key was pressed to quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    # In headless mode, check for keyboard interrupt
                    time.sleep(0.01)  # Small sleep to prevent CPU overuse
                    
        except KeyboardInterrupt:
            print("Interrupted by user.")
        finally:
            self.stop()
            # Disconnect from Arduino if connected
            if self.arduino_serial:
                self.arduino_serial.disconnect()
    
    def _display_info(self, frame, prediction, confidence, fps=None):
        """
        Display information on screen.
        
        Args:
            frame (numpy.ndarray): Current frame
            prediction (str): Current prediction
            confidence (float): Prediction confidence
            fps (float, optional): Current FPS
        """
        # Text settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        text_color = (255, 255, 255)  # White
        bg_color = (0, 0, 0)  # Black
        
        # Add prediction information
        prediction_text = f"Prediction: {prediction}"
        confidence_text = f"Confidence: {confidence:.2f}"
        
        # Add information about the command sent to Arduino
        arduino_text = ""
        if self.arduino_serial and prediction == "Good":
            arduino_text = "Arduino: Sending 1"
        elif self.arduino_serial and prediction == "Bad":
            arduino_text = "Arduino: Sending 0"
        
        # Text position
        y_pos = 30
        
        # Function to add text with background
        def add_text_with_background(text, y):
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            cv2.rectangle(frame, (10, y - 25), (10 + text_size[0], y + 5), bg_color, -1)
            cv2.putText(frame, text, (10, y), font, font_scale, text_color, font_thickness)
            return y + 40
        
        # Add texts
        y_pos = add_text_with_background(prediction_text, y_pos)
        y_pos = add_text_with_background(confidence_text, y_pos)
        
        # Add Arduino text if available
        if arduino_text:
            y_pos = add_text_with_background(arduino_text, y_pos)
        
        # Add FPS if available
        if fps is not None:
            fps_text = f"FPS: {fps:.1f}"
            add_text_with_background(fps_text, y_pos) 