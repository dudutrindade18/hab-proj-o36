#!/bin/bash

# HAB Project - Raspberry Pi Setup Script
# This script sets up the environment for running the HAB Project on Raspberry Pi 4B

echo "===== HAB Project - Raspberry Pi Setup ====="
echo "This script will install all necessary dependencies for running the project on Raspberry Pi 4B."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi. The script might not work correctly."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    libatlas-base-dev \
    libjpeg-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libwebp-dev \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    git \
    curl \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    libgtk2.0-dev \
    pkg-config \
    cmake \
    libgtk-3-dev \
    python3-dev \
    python3-numpy

# Rebuild and install OpenCV with GUI support
echo "Building OpenCV with GUI support..."
# Remove existing OpenCV packages
sudo apt-get remove -y python3-opencv
sudo apt-get autoremove -y

# Install OpenCV from pip with GUI support
python -m pip install --upgrade pip
python -m pip install opencv-python

# Install pyenv
echo "Installing pyenv..."
if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
    
    # Add pyenv to PATH and initialize
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    
    # If using zsh, also add to zshrc
    if [ -f "$HOME/.zshrc" ]; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
        echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
        echo 'eval "$(pyenv init -)"' >> ~/.zshrc
    fi
    
    # Load pyenv for the current session
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
else
    echo "pyenv is already installed."
fi

# Check if .python-version file exists
if [ -f ".python-version" ]; then
    PYTHON_VERSION=$(cat .python-version)
    echo "Found .python-version file. Installing Python $PYTHON_VERSION..."
    
    # Install the Python version specified in .python-version
    pyenv install -s $PYTHON_VERSION
    pyenv local $PYTHON_VERSION
else
    # Default to Python 3.9.0 if no .python-version file
    echo "No .python-version file found. Installing Python 3.9.0..."
    pyenv install -s 3.9.0
    pyenv local 3.9.0
fi

# Verify Python version
PYTHON_VERSION=$(python --version)
echo "Using Python: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify we're using the virtual environment's Python
VENV_PYTHON=$(which python)
if [[ $VENV_PYTHON != *"venv"* ]]; then
    echo "Error: Virtual environment not properly activated"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Setup permissions for camera and serial ports
echo "Setting up permissions..."
sudo usermod -a -G video $USER
sudo usermod -a -G dialout $USER

# Convert Keras model to TFLite if needed
if [ -f "converted_keras/keras_model.h5" ] && [ ! -f "converted_keras/model.tflite" ]; then
    echo "Converting Keras model to TFLite format..."
    # We'll create a temporary Python script to convert the model
    cat > convert_model.py << 'EOF'
import tensorflow as tf

# Load the Keras model
model = tf.keras.models.load_model('converted_keras/keras_model.h5')

# Convert the model to TFLite format
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TFLite model
with open('converted_keras/model.tflite', 'wb') as f:
    f.write(tflite_model)

print("Model converted successfully!")
EOF

    # Try to install TensorFlow temporarily for conversion
    pip install tensorflow
    python convert_model.py
    pip uninstall -y tensorflow
    rm convert_model.py
fi

# Make main.py executable
chmod +x main.py

echo "===== Setup Complete! ====="
echo "You may need to log out and log back in for permission changes to take effect."
echo "Also, restart your shell or run 'source ~/.bashrc' to activate pyenv."
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python main.py"
echo ""
echo "Note: The first run may take some time as the model initializes." 