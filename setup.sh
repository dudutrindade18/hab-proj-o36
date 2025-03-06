#!/bin/bash

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

# Install requirements
echo "Installing requirements..."
python -m pip install --upgrade pip  # Ensure pip is up to date
python -m pip install -r requirements.txt

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate  # If not already activated"
echo "python main.py"

# Make main.py executable
chmod +x main.py

echo "Note: The first execução may take some time as TensorFlow initializes."