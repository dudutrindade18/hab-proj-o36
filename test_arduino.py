#!/usr/bin/env python3
"""
Test script for sending commands to Arduino.
This script allows testing the serial communication with Arduino without
needing to run the entire classification system with the camera.
"""

import argparse
import time
import serial
import serial.tools.list_ports
import threading
import sys
import re

# Common vendor and product IDs for Arduino boards
ARDUINO_VID_PID_PATTERNS = [
    # Arduino Uno, Nano, etc.
    r'VID:PID=2341:00[0-9a-fA-F]{2}',  # Official Arduino
    r'VID:PID=1A86:7523',              # CH340 (clones)
    r'VID:PID=0403:6001',              # FTDI (some clones)
    r'VID:PID=0403:6015',              # FTDI (some clones)
    r'VID:PID=1A86:55D4',              # CH9102 (some clones)
]

def find_arduino_port():
    """
    Try to find Arduino port automatically.
    
    Returns:
        str or None: Arduino port or None if not found
    """
    # List all available serial ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No serial ports found in the system.")
        return None
        
    print(f"Available serial ports: {len(ports)}")
    for port in ports:
        print(f"- {port.device}: {port.description} (hwid: {port.hwid})")
    
    # Strategy 1: Look for ports with descriptions or hwid containing "Arduino"
    for port in ports:
        if "arduino" in port.description.lower() or "arduino" in port.hwid.lower():
            print(f"Arduino found on port {port.device} (description/hwid contains 'Arduino')")
            return port.device
    
    # Strategy 2: Look for known Arduino VID:PIDs
    for port in ports:
        for pattern in ARDUINO_VID_PID_PATTERNS:
            if re.search(pattern, port.hwid, re.IGNORECASE):
                print(f"Arduino found on port {port.device} (VID:PID matches an Arduino)")
                return port.device
    
    # Strategy 3: Look for ports with common Arduino names
    arduino_port_patterns = [
        r'(cu|tty)\.usbmodem\d+',  # macOS/Linux Arduino
        r'(cu|tty)\.wchusbserial\d+',  # macOS/Linux CH340
        r'(cu|tty)\.SLAB_USBtoUART',  # macOS/Linux CP210x
        r'COM\d+',  # Windows
    ]
    
    for port in ports:
        for pattern in arduino_port_patterns:
            if re.match(pattern, port.device):
                print(f"Possible Arduino found on port {port.device} (port name matches an Arduino pattern)")
                return port.device
    
    # Strategy 4: If all else fails and there's only one port, use it
    if len(ports) == 1:
        print(f"Arduino not explicitly identified, but only one port is available: {ports[0].device}")
        return ports[0].device
        
    # If we get here, we couldn't identify the Arduino
    print("Could not identify an Arduino port. Available ports:")
    for port in ports:
        print(f"- {port.device}: {port.description} (hwid: {port.hwid})")
    
    return None

def serial_reader(ser, stop_event):
    """
    Function to continuously read from the serial port in a separate thread.
    
    Args:
        ser (serial.Serial): Serial connection object
        stop_event (threading.Event): Event to signal when to stop the thread
    """
    print("Starting serial port reading. Press Ctrl+C to exit.")
    try:
        while not stop_event.is_set():
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Arduino: {line}")
            time.sleep(0.1)  # Small pause to avoid overloading the CPU
    except Exception as e:
        print(f"Error in reading thread: {e}")

def verify_arduino_connection(ser):
    """
    Check if Arduino is actually connected and responding.
    
    Args:
        ser (serial.Serial): Serial connection object
        
    Returns:
        bool: True if Arduino is responding, False otherwise
    """
    # Clear input buffer
    ser.reset_input_buffer()
    
    # Send a ping command
    print("Verifying connection with Arduino...")
    
    # Send multiple pings to increase the chance of response
    for attempt in range(3):
        print(f"Attempt {attempt+1}/3...")
        ser.write(b"ping\n")
        ser.flush()
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < 1:  # 1 second timeout per attempt
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if "Arduino ready" in response:
                    print("Arduino connected and responding!")
                    return True
                else:
                    print(f"Response received: {response}")
            time.sleep(0.1)
    
    print("WARNING: Arduino did not respond to ping. The serial port is open, but Arduino may not be connected or not running the correct code.")
    return False

def send_command(port, command, baudrate=9600, monitor_mode=False):
    """
    Send a command to Arduino and optionally monitor the serial port.
    
    Args:
        port (str): Arduino serial port
        command (int): Command to send (0 or 1)
        baudrate (int): Baud rate
        monitor_mode (bool): Whether to enter continuous monitoring mode
    """
    try:
        # Connect to serial port
        print(f"Trying to connect to port {port}...")
        ser = serial.Serial(port, baudrate, timeout=2)
        print(f"Serial port {port} opened with baudrate {baudrate}")
        
        # Wait for Arduino initialization
        time.sleep(2)
        
        # Check if Arduino is actually connected and responding
        arduino_connected = verify_arduino_connection(ser)
        
        # If Arduino is not responding and we're in monitor mode, don't continue
        if not arduino_connected and monitor_mode:
            print("Error: Cannot enter monitoring mode without a connected Arduino.")
            ser.close()
            return
        
        # If Arduino is not responding but we're not in monitor mode, warn but continue
        if not arduino_connected and not monitor_mode:
            print("Continuing even without Arduino confirmation...")
        
        # Send the command
        cmd_str = str(command) + '\n'
        print(f"Sending command: {command}")
        ser.write(cmd_str.encode())
        
        # If not in monitor mode, just read the immediate response
        if not monitor_mode:
            # Wait and read the response
            time.sleep(0.5)
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Response from Arduino: {response}")
            else:
                print("No response received from Arduino.")
            
            # Close the connection
            ser.close()
            print("Connection closed")
        else:
            # Enter continuous monitoring mode
            stop_event = threading.Event()
            reader_thread = threading.Thread(target=serial_reader, args=(ser, stop_event))
            reader_thread.daemon = True
            reader_thread.start()
            
            print("Monitoring mode activated. Press Ctrl+C to exit.")
            print("You can send additional commands by typing '0' or '1' followed by Enter:")
            
            try:
                while True:
                    # Read user input
                    user_input = input()
                    if user_input.strip() in ['0', '1']:
                        cmd = user_input.strip() + '\n'
                        ser.write(cmd.encode())
                        print(f"Command sent: {user_input.strip()}")
                    elif user_input.lower() == 'exit' or user_input.lower() == 'quit':
                        break
                    else:
                        print("Invalid command. Use '0' or '1', or 'exit' to quit.")
            except KeyboardInterrupt:
                print("\nInterrupted by user.")
            finally:
                # Stop the reading thread and close the connection
                stop_event.set()
                reader_thread.join(timeout=1.0)
                ser.close()
                print("Connection closed")
        
    except serial.SerialException as e:
        print(f"Error connecting or sending command: {e}")
        print("Check if Arduino is connected and if the port is correct.")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Connection closed")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Arduino Communication Test')
    
    # Create a mutually exclusive group of arguments
    group = parser.add_mutually_exclusive_group(required=True)
    
    # Add the command as an optional argument within the group
    group.add_argument('--command', type=int, choices=[0, 1],
                      help='Command to send (0: Turn OFF LED, 1: Turn ON LED)')
    
    # Add the --list-ports option to the mutually exclusive group
    group.add_argument('--list-ports', action='store_true',
                      help='List all available serial ports and exit')
    
    parser.add_argument('--port', type=str, default=None,
                        help='Arduino serial port (e.g., /dev/ttyUSB0, COM3). If not specified, will try to detect automatically.')
    
    parser.add_argument('--baudrate', type=int, default=9600,
                        help='Baud rate for serial communication (default: 9600)')
    
    parser.add_argument('--monitor', action='store_true',
                        help='Activate continuous monitoring mode for the serial port')
    
    args = parser.parse_args()
    
    # If the --list-ports option was specified, just list the ports and exit
    if args.list_ports:
        find_arduino_port()
        return
    
    # If port was not specified, try to find it automatically
    if args.port is None:
        args.port = find_arduino_port()
        if args.port is None:
            print("Error: Could not find Arduino. Check the connection or specify the port manually.")
            return
    
    # Send the command and optionally monitor the serial port
    send_command(args.port, args.command, args.baudrate, args.monitor)

if __name__ == "__main__":
    main() 