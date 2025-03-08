"""
Module for managing serial communication with Arduino.
"""

import serial
import time
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArduinoSerial:
    """Class for managing serial communication with Arduino."""
    
    # Common vendor and product IDs for Arduino boards
    ARDUINO_VID_PID_PATTERNS = [
        # Arduino Uno, Nano, etc.
        r'VID:PID=2341:00[0-9a-fA-F]{2}',  # Official Arduino
        r'VID:PID=1A86:7523',              # CH340 (clones)
        r'VID:PID=0403:6001',              # FTDI (some clones)
        r'VID:PID=0403:6015',              # FTDI (some clones)
        r'VID:PID=1A86:55D4',              # CH9102 (some clones)
    ]
    
    def __init__(self, port=None, baudrate=9600, timeout=1, require_arduino=True):
        """
        Initialize serial communication with Arduino.
        
        Args:
            port (str, optional): Serial port (e.g., '/dev/ttyUSB0', 'COM3'). 
                                 If None, will try to detect automatically.
            baudrate (int): Baud rate
            timeout (float): Timeout for read operations in seconds
            require_arduino (bool): If True, requires Arduino to be actually connected and responding
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_connected = False
        self.arduino_responding = False
        self.require_arduino = require_arduino
        
    def connect(self):
        """
        Connect to Arduino.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if self.is_connected:
            return True
            
        try:
            # If port is not specified, try to find it automatically
            if self.port is None:
                self.port = self._find_arduino_port()
                if self.port is None:
                    logger.error("Could not find Arduino. Check the connection.")
                    return False
            
            # Connect to serial port
            logger.info(f"Trying to connect to port {self.port}...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Wait for Arduino initialization (important for boards that reset on connect)
            time.sleep(2)
            
            # Check if Arduino is actually responding
            self.arduino_responding = self._verify_arduino_connection()
            
            # If Arduino is not responding and it's required, fail the connection
            if not self.arduino_responding and self.require_arduino:
                logger.error("Arduino is not responding. Check the physical connection and the code on Arduino.")
                self.serial_conn.close()
                return False
            
            self.is_connected = True
            if self.arduino_responding:
                logger.info(f"Connected to Arduino on port {self.port} and Arduino is responding")
            else:
                logger.warning(f"Serial port {self.port} is open, but Arduino is not responding. Check the physical connection and the code on Arduino.")
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"Error connecting to Arduino: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino."""
        if self.serial_conn and self.is_connected:
            self.serial_conn.close()
            self.is_connected = False
            self.arduino_responding = False
            logger.info("Disconnected from Arduino")
    
    def _verify_arduino_connection(self):
        """
        Check if Arduino is actually connected and responding.
        
        Returns:
            bool: True if Arduino is responding, False otherwise
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False
            
        # Clear input buffer
        self.serial_conn.reset_input_buffer()
        
        # Send a ping command
        logger.info("Verifying connection with Arduino...")
        try:
            # Send multiple pings to increase the chance of response
            for _ in range(3):
                self.serial_conn.write(b"ping\n")
                self.serial_conn.flush()
                
                # Wait for response
                start_time = time.time()
                while time.time() - start_time < 1:  # 1 second timeout per attempt
                    if self.serial_conn.in_waiting:
                        response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        if "Arduino ready" in response:
                            logger.info("Arduino connected and responding!")
                            return True
                        else:
                            logger.info(f"Response received: {response}")
                    time.sleep(0.1)
            
            logger.warning("Arduino did not respond to ping. The serial port is open, but Arduino may not be connected or not running the correct code.")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying connection with Arduino: {e}")
            return False
    
    def send_command(self, command):
        """
        Send a command to Arduino.
        
        Args:
            command: Command to send (will be converted to string and terminated with newline)
            
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        if not self.is_connected:
            if not self.connect():
                return False
        
        # If Arduino is not responding and it's required, don't send the command
        if not self.arduino_responding and self.require_arduino:
            logger.error("Cannot send command: Arduino is not responding")
            return False
        
        try:
            # Convert command to string and add newline
            cmd_str = str(command) + '\n'
            # Send command as bytes
            self.serial_conn.write(cmd_str.encode())
            self.serial_conn.flush()
            logger.debug(f"Command sent: {command}")
            
            # If Arduino is responding, wait and read the response
            if self.arduino_responding:
                time.sleep(0.5)
                if self.serial_conn.in_waiting:
                    response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    logger.debug(f"Response from Arduino: {response}")
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"Error sending command: {e}")
            self.is_connected = False
            return False
    
    def send_label_command(self, label):
        """
        Send a command based on the model's label.
        
        Args:
            label (str): Model label ('Good', 'Bad', 'Nothing')
            
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        if label == "Good":
            logger.info("Label 'Good' detected. Sending command '1'")
            return self.send_command(1)
        elif label == "Bad":
            logger.info("Label 'Bad' detected. Sending command '0'")
            return self.send_command(0)
        elif label == "Nothing":
            logger.debug("Label 'Nothing' detected. No command sent.")
            return True
        else:
            logger.warning(f"Unknown label: {label}. No command sent.")
            return False
    
    def _find_arduino_port(self):
        """
        Try to find Arduino port automatically.
        
        Returns:
            str or None: Arduino port or None if not found
        """
        import serial.tools.list_ports
        
        # List all available serial ports
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            logger.error("No serial ports found in the system.")
            return None
            
        logger.info(f"Available serial ports: {len(ports)}")
        for port in ports:
            logger.info(f"- {port.device}: {port.description} (hwid: {port.hwid})")
        
        # Strategy 1: Look for ports with descriptions or hwid containing "Arduino"
        for port in ports:
            if "arduino" in port.description.lower() or "arduino" in port.hwid.lower():
                logger.info(f"Arduino found on port {port.device} (description/hwid contains 'Arduino')")
                return port.device
        
        # Strategy 2: Look for known Arduino VID:PIDs
        for port in ports:
            for pattern in self.ARDUINO_VID_PID_PATTERNS:
                if re.search(pattern, port.hwid, re.IGNORECASE):
                    logger.info(f"Arduino found on port {port.device} (VID:PID matches an Arduino)")
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
                    logger.info(f"Possible Arduino found on port {port.device} (port name matches an Arduino pattern)")
                    return port.device
        
        # Strategy 4: If all else fails and there's only one port, use it
        if len(ports) == 1:
            logger.warning(f"Arduino not explicitly identified, but only one port is available: {ports[0].device}")
            return ports[0].device
            
        # If we get here, we couldn't identify the Arduino
        logger.error("Could not identify an Arduino port. Available ports:")
        for port in ports:
            logger.error(f"- {port.device}: {port.description} (hwid: {port.hwid})")
        
        return None 