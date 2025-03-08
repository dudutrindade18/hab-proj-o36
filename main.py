#!/usr/bin/env python3
"""
HAB Project - AI Classification System
Main application that integrates camera and AI model.
"""

import os
import argparse
from hab_proj.model import AIModel
from hab_proj.camera import Camera
from hab_proj.serial_comm import ArduinoSerial

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='HAB Project - AI Classification System')
    
    parser.add_argument('--camera', type=int, default=0,
                        help='Camera ID (default: 0, usually the built-in webcam)')
    
    parser.add_argument('--model', type=str, default='converted_keras/keras_model.h5',
                        help='Path to the model file (default: converted_keras/keras_model.h5)')
    
    parser.add_argument('--labels', type=str, default='converted_keras/labels.txt',
                        help='Path to the labels file (default: converted_keras/labels.txt)')
    
    parser.add_argument('--interval', type=float, default=0.5,
                        help='Interval in seconds between predictions (default: 0.5)')
    
    parser.add_argument('--no-fps', action='store_true',
                        help='Do not display FPS on screen')
    
    # Arguments for Arduino serial communication
    parser.add_argument('--no-arduino', action='store_true',
                        help='Disable Arduino communication (by default, communication is enabled)')
    
    parser.add_argument('--port', type=str, default=None,
                        help='Arduino serial port (e.g., /dev/ttyUSB0, COM3). If not specified, will try to detect automatically.')
    
    parser.add_argument('--baudrate', type=int, default=9600,
                        help='Baud rate for serial communication (default: 9600)')
    
    parser.add_argument('--allow-no-arduino', action='store_true',
                        help='Allow execution even if Arduino is not responding')
    
    return parser.parse_args()

def main():
    """Main function of the application."""
    # Parse arguments
    args = parse_args()
    
    # Check if model files exist
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        return
    
    if not os.path.exists(args.labels):
        print(f"Error: Labels file not found: {args.labels}")
        return
    
    try:
        # Load the AI model
        print(f"Loading AI model from {args.model}...")
        model = AIModel(args.model, args.labels)
        print("Model loaded successfully!")
        
        # Initialize Arduino serial communication (by default)
        arduino_serial = None
        if not args.no_arduino:
            print("Initializing Arduino communication...")
            arduino_serial = ArduinoSerial(
                port=args.port,
                baudrate=args.baudrate,
                require_arduino=not args.allow_no_arduino
            )
            
            # Try to connect to Arduino
            if arduino_serial.connect():
                if arduino_serial.arduino_responding:
                    print(f"Arduino connected and responding on port {arduino_serial.port}")
                else:
                    if args.allow_no_arduino:
                        print("Warning: Arduino is not responding, but continuing anyway because --allow-no-arduino was specified.")
                    else:
                        print("Error: Arduino is not responding. Use --allow-no-arduino to continue anyway.")
                        return
            else:
                print("Error: Could not connect to Arduino.")
                if not args.allow_no_arduino:
                    print("Use --no-arduino to run without Arduino or --allow-no-arduino to continue even without connection.")
                    return
                else:
                    arduino_serial = None
        else:
            print("Arduino communication disabled.")
        
        # Initialize the camera with the model and Arduino
        camera = Camera(
            camera_id=args.camera, 
            model=model,
            arduino_serial=arduino_serial
        )
        
        # Run the camera with the model
        print(f"Starting camera {args.camera} with real-time classification...")
        if arduino_serial and arduino_serial.arduino_responding:
            print("Arduino communication enabled. Sending commands based on predictions:")
            print("  - 'Good' -> Sends '1'")
            print("  - 'Bad' -> Sends '0'")
            print("  - 'Nothing' -> Sends nothing")
        
        print("Press 'q' to quit.")
        
        camera.run_with_model(
            display_fps=not args.no_fps,
            prediction_interval=args.interval
        )
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 