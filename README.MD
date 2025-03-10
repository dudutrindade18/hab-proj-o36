# HAB Project - AI Classification System

This project integrates a camera with an AI model for real-time classification. The system captures images from the webcam, processes them using a trained AI model, and displays the results on screen. It also supports serial communication with Arduino to send commands based on the classifications.

## Project Structure

```
hab-proj-o36/
├── arduino_code/          # Folder with Arduino code
│   └── hab_proj_receiver.ino  # Arduino code to receive commands
├── converted_keras/       # Folder with the AI model
│   ├── keras_model.h5     # Keras model file
│   └── labels.txt         # Model labels file
├── hab_proj/              # Main project package
│   ├── __init__.py        # Package initialization file
│   ├── camera.py          # Module for managing the camera
│   ├── model.py           # Module for managing the AI model
│   └── serial_comm.py     # Module for Arduino serial communication
├── main.py                # Application entry point
├── requirements.txt       # Project dependencies
├── setup.sh               # Setup script for regular systems
├── setup_raspberry.sh     # Setup script for Raspberry Pi
├── test_arduino.py        # Script for testing Arduino communication
└── webcam.py              # Original webcam script (kept for reference)
```

## Requirements

- Python 3.9 (managed by pyenv)
- OpenCV
- TensorFlow (regular systems) or TensorFlow Lite (Raspberry Pi)
- NumPy
- Pillow
- PySerial (for Arduino communication)

## Installation

### Regular Systems

1. Clone the repository:
   ```
   git clone <https://github.com/dudutrindade18/hab-proj-o36>
   cd hab-proj-o36
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```
   This script will:
   - Create a Python virtual environment
   - Activate the virtual environment
   - Install all necessary dependencies
   - Make the main.py file executable

3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

### Raspberry Pi

1. Clone the repository:
   ```
   git clone <https://github.com/dudutrindade18/hab-proj-o36>
   cd hab-proj-o36
   ```

2. Run the Raspberry Pi setup script:
   ```
   chmod +x setup_raspberry.sh
   ./setup_raspberry.sh
   ```
   This script will:
   - Install system dependencies required for OpenCV and TensorFlow Lite
   - Install and configure pyenv for Python version management
   - Install the Python version specified in `.python-version` (or default to Python 3.9.0)
   - Create a Python virtual environment
   - Install Python dependencies
   - Set up permissions for camera and serial ports
   - Convert the Keras model to TensorFlow Lite format if needed
   - Make the main.py file executable

3. Restart your shell or source your profile to activate pyenv:
   ```
   source ~/.bashrc  # or ~/.zshrc if using zsh
   ```

4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

5. Log out and log back in for permission changes to take effect (or reboot):
   ```
   sudo reboot
   ```

## Usage

Run the main program:

```
python main.py
```

By default, the program will try to connect to Arduino. If you don't have an Arduino connected, use the `--no-arduino` option.

### Command Line Options

#### General Options
- `--camera`: Camera ID (default: 0, usually the built-in webcam)
- `--model`: Path to the model file (default: converted_keras/keras_model.h5)
- `--labels`: Path to the labels file (default: converted_keras/labels.txt)
- `--interval`: Interval in seconds between predictions (default: 0.5)
- `--no-fps`: Do not display FPS on screen

#### Arduino Options
- `--no-arduino`: Disable Arduino communication (by default, communication is enabled)
- `--port`: Arduino serial port (e.g., /dev/ttyUSB0, COM3). If not specified, will try to detect automatically.
- `--baudrate`: Baud rate for serial communication (default: 9600)
- `--allow-no-arduino`: Allow execution even if Arduino is not responding

#### Raspberry Pi Specific Options
- `--width`: Camera capture width (default: 640)
- `--height`: Camera capture height (default: 480)
- `--low-power`: Enable low power mode (reduces resolution to 320x240 and prediction frequency)
- `--headless`: Run in headless mode (no GUI, useful for Raspberry Pi without display)

### Examples

Run with default webcam (with Arduino, if available):
```
python main.py
```

Run without Arduino:
```
python main.py --no-arduino
```

Specify Arduino port:
```
python main.py --port /dev/ttyUSB0
```

Use external camera and faster prediction interval:
```
python main.py --camera 1 --interval 0.2
```

Allow execution even without Arduino responding:
```
python main.py --allow-no-arduino
```

Run on Raspberry Pi in low power mode:
```
python main.py --low-power
```

Run on Raspberry Pi without display:
```
python main.py --headless
```

## Raspberry Pi Tips

### Python Version Management

The project uses pyenv to manage Python versions. The setup script will:

1. Install pyenv if not already installed
2. Read the Python version from the `.python-version` file
3. Install that specific Python version
4. Set it as the local Python version for the project

If you need to change the Python version:
```
pyenv install 3.9.0  # Install a specific version
pyenv local 3.9.0    # Set it as the local version for this project
```

### Camera Setup

1. Enable the camera interface:
   ```
   sudo raspi-config
   ```
   Navigate to "Interface Options" > "Camera" and enable it.

2. If using a USB webcam, make sure it's compatible with Raspberry Pi. Most USB webcams should work.

3. For better performance, consider reducing the resolution:
   ```
   python main.py --width 320 --height 240
   ```

### Running Without Display

If you're running the Raspberry Pi without a display (headless mode):

1. Use the `--headless` option:
   ```
   python main.py --headless
   ```

2. You can still see the predictions in the terminal output.

3. For remote access, consider using SSH with X forwarding:
   ```
   ssh -X pi@your_raspberry_pi_ip
   ```

### Performance Optimization

1. Use the `--low-power` option for better performance:
   ```
   python main.py --low-power
   ```

2. Increase the prediction interval to reduce CPU usage:
   ```
   python main.py --interval 1.0
   ```

3. If you're only interested in the Arduino control, use both headless and low-power modes:
   ```
   python main.py --headless --low-power
   ```

## Testing Arduino Communication

To test Arduino communication without running the entire classification system, use the `test_arduino.py` script:

### List Available Ports

To list all available serial ports and identify Arduino:

```
python test_arduino.py --list-ports
```

### Send Commands

To send commands to Arduino:

```
python test_arduino.py --command [0|1] [options]
```

#### Options

- `--port`: Arduino serial port (e.g., /dev/ttyUSB0, COM3). If not specified, will try to detect automatically.
- `--baudrate`: Baud rate for serial communication (default: 9600)
- `--monitor`: Activate continuous monitoring mode for the serial port

#### Examples

Turn ON the LED (send command 1):
```
python test_arduino.py --command 1
```

Turn OFF the LED (send command 0):
```
python test_arduino.py --command 0
```

Specify port manually:
```
python test_arduino.py --command 1 --port /dev/ttyUSB0
```

Monitor the serial port continuously:
```
python test_arduino.py --command 1 --monitor
```

### Monitoring Mode

When you use the `--monitor` option, the script enters an interactive mode that:

1. Sends the initial specified command
2. Continuously monitors all messages sent by Arduino
3. Allows sending additional commands by typing '0' or '1' followed by Enter
4. Continues until you press Ctrl+C or type 'exit'

This mode is useful for:
- Debugging Arduino communication
- Testing different commands in sequence
- Monitoring Arduino responses in real-time

**Note**: Monitoring mode only works if a real Arduino is connected and responding. The script will check this before entering monitoring mode.

## Arduino Connection Verification

The system now verifies if Arduino is actually connected and responding, not just if the serial port can be opened. This is done by sending a "ping" command and waiting for a specific response.

If Arduino is not responding:
- The test script will not enter monitoring mode
- The main program will not start, unless you use the `--allow-no-arduino` option

This prevents situations where the program appears to be working, but there's actually no Arduino connected or the Arduino is not running the correct code.

## Automatic Port Detection

The system uses several strategies to automatically detect the Arduino port:

1. Looks for ports with "Arduino" in the description or hardware ID
2. Looks for known Arduino VID:PIDs (vendor and product identifiers)
3. Looks for ports with common Arduino name patterns
4. If there's only one port available, uses it as a last resort

This makes the system more robust across different operating systems and with different types of Arduino boards.

## How It Works

1. The program loads the specified AI model.
2. By default, it tries to connect to Arduino and verifies if it's responding (unless `--no-arduino` is specified).
3. Initializes the camera and starts capturing frames.
4. At regular intervals, the current frame is processed by the AI model.
5. The classification result is displayed on screen along with the prediction confidence.
6. If connected to Arduino, sends commands based on the classification:
   - "Good" -> Sends '1'
   - "Bad" -> Sends '0'
   - "Nothing" -> Sends nothing
7. Press 'q' to quit the program.

## Arduino Communication

The system sends commands to Arduino based on the model's classifications:

- When classification is "Good", sends value "1"
- When classification is "Bad", sends value "0"
- When classification is "Nothing", sends nothing

### Arduino Setup

For Arduino to correctly receive commands:

1. Open the `arduino_code/hab_proj_receiver.ino` file in Arduino IDE
2. Upload the code to your Arduino
3. Connect Arduino to computer via USB
4. Run the Python application (main.py)

The Arduino code is configured to:
- Initialize serial communication at 9600 baud
- Blink the LED 3 times at startup to indicate it's ready
- Respond to "ping" commands for connection verification
- Turn ON the built-in LED when receiving command "1" (classification "Good")
- Turn OFF the built-in LED when receiving command "0" (classification "Bad")
- Send confirmation via serial after each action

## Model Classes

The current model classifies images into three categories:
- 0: Good
- 1: Bad
- 2: Nothing

## Development

### Main Modules

#### hab_proj.model.AIModel

Class responsible for loading and using the AI model for classification.

Main methods:
- `__init__(model_path, labels_path)`: Initializes the model
- `predict(image)`: Makes a prediction on an image

#### hab_proj.camera.Camera

Class for managing the camera and integrating with the AI model.

Main methods:
- `__init__(camera_id, model, arduino_serial)`: Initializes the camera
- `start()`: Starts the camera
- `stop()`: Releases camera resources
- `run_with_model(display_fps, prediction_interval, headless)`: Runs the camera with the AI model

#### hab_proj.serial_comm.ArduinoSerial

Class for managing serial communication with Arduino.

Main methods:
- `__init__(port, baudrate, timeout, require_arduino)`: Initializes serial communication
- `connect()`: Connects to Arduino and verifies if it's responding
- `disconnect()`: Disconnects from Arduino
- `send_command(command)`: Sends a command to Arduino
- `send_label_command(label)`: Sends a command based on the model's label
