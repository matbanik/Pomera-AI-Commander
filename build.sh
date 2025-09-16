#!/bin/bash

# Build script for promera_ai on macOS
# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
SETUP_FILE="setup.py"
APP_NAME="promera_ai"
VENV_DIR="venv_build"

# --- Functions ---
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: '$1' is not installed or not in your PATH."
        exit 1
    fi
}

# --- Main Script ---
echo "--- Starting build process for $APP_NAME ---"

# Check for prerequisites
check_command python3
check_command pip3

# Set up a virtual environment for a clean build
if [ -d "$VENV_DIR" ]; then
    echo "--- Removing existing build virtual environment. ---"
    rm -rf "$VENV_DIR"
fi
echo "--- Creating a new virtual environment in '$VENV_DIR'... ---"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install required Python packages
echo "--- Installing build dependencies... ---"
pip3 install -U pip
pip3 install py2app
pip3 install requests reportlab python-docx pyaudio numpy Metaphone lemminflect huggingface_hub

# Check for the main script
if [ ! -f "$SETUP_FILE" ]; then
    echo "Error: The setup script '$SETUP_FILE' was not found in the current directory."
    deactivate
    exit 1
fi

# Run py2app to build the application
echo "--- Running py2app to build the application bundle... ---"
python3 "$SETUP_FILE" py2app

# Clean up
echo "--- Deactivating virtual environment. ---"
deactivate

# --- Success Message ---
echo ""
echo "--------------------------------------------------------"
echo " Build successful!"
echo " The application bundle can be found in the 'dist' directory:"
echo "   dist/$APP_NAME.app"
echo " You can now drag '$APP_NAME.app' to your Applications folder."
echo " The build artifacts are in the 'build' and '$VENV_DIR' directories."
echo " You can remove them if you no longer need them."
echo "--------------------------------------------------------"