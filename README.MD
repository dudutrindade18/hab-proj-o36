# Webcam Viewer

A simple Python application that displays your webcam feed using OpenCV.

## Prerequisites

- Python (managed by pyenv or your preferred Python version manager)
- macOS with a working webcam
- Terminal access

## Project Structure

```
.
├── README.md
├── requirements.txt    # Project dependencies
├── setup.sh           # Setup script for virtual environment
└── webcam.py          # Main application script
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Make the setup script executable:
```bash
chmod +x setup.sh
```

3. Run the setup script to create a virtual environment and install dependencies:
```bash
./setup.sh
```

This script will:
- Create a new virtual environment in the `venv` directory
- Activate the virtual environment
- Install required dependencies from `requirements.txt`

## Usage

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Run the webcam viewer:
```bash
python webcam.py
```

3. Use the application:
   - A window will open showing your webcam feed
   - Press 'q' to quit the application

4. When you're done, you can deactivate the virtual environment:
```bash
deactivate
```

## Dependencies

The project uses the following main dependencies:
- OpenCV Python (opencv-python): Version 4.5.5.64
- NumPy: Version 1.24.3 (OpenCV is not yet fully compatible with NumPy 2.x)

Dependencies are managed through the `requirements.txt` file and are automatically installed during setup.

## Troubleshooting

If you encounter any issues:

1. Make sure your webcam is not being used by another application
2. Check if your webcam is properly connected and recognized by your system
3. Ensure you have the necessary permissions for webcam access
4. If you see NumPy-related errors, ensure you're using the version specified in requirements.txt (1.24.3)

If you see "Error: Could not access the webcam", try closing other applications that might be using the webcam.

## License

[Your chosen license]
