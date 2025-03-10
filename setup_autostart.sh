#!/bin/bash

# HAB Project - Autostart Setup Script
# This script sets up the HAB Project to start automatically on boot

echo "===== HAB Project - Autostart Setup ====="

# Get the current username
CURRENT_USER=$(whoami)
PROJECT_DIR=$(pwd)

# Update the service file with the correct username and paths
sed -i "s|User=hab-proj5|User=$CURRENT_USER|g" hab_proj_autostart.service
sed -i "s|/home/hab-proj5/Desktop/hab-proj-o36|$PROJECT_DIR|g" hab_proj_autostart.service

# Check if we want to run in headless mode
read -p "Run in headless mode (no GUI display)? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    # Remove the --headless flag if not running in headless mode
    sed -i "s| --headless||g" hab_proj_autostart.service
fi

# Add any additional command line arguments
read -p "Add any additional command line arguments (e.g., --low-power): " ARGS
if [ ! -z "$ARGS" ]; then
    # Add the additional arguments to the ExecStart line
    sed -i "s|main.py.*|main.py $ARGS|g" hab_proj_autostart.service
fi

# Copy the service file to the systemd directory
echo "Installing systemd service..."
sudo cp hab_proj_autostart.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable hab_proj_autostart.service

echo "Service installed and enabled to start on boot."
echo "To start the service now, run: sudo systemctl start hab_proj_autostart.service"
echo "To check status, run: sudo systemctl status hab_proj_autostart.service"
echo "To stop the service, run: sudo systemctl stop hab_proj_autostart.service"
echo "To disable autostart, run: sudo systemctl disable hab_proj_autostart.service"

# Ask if we want to start the service now
read -p "Start the service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start hab_proj_autostart.service
    echo "Service started. Check status with: sudo systemctl status hab_proj_autostart.service"
fi 