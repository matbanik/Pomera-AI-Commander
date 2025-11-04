#!/bin/bash

echo "Building Pomera AI Commander with PyInstaller..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PyInstaller"
        exit 1
    fi
fi

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install requirements"
        exit 1
    fi
fi

# Clean previous build
rm -rf build dist

echo
echo "Building executable with PyInstaller..."
echo "Command: pyinstaller --onedir [with many exclusions] --name pomera pomera.py"

python3 -m PyInstaller --onedir --exclude-module pytest --exclude-module test --exclude-module tests --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module jupyter --exclude-module IPython --exclude-module torch --exclude-module torchvision --exclude-module torchaudio --exclude-module tensorflow --exclude-module sklearn --exclude-module cv2 --exclude-module numpy --exclude-module pygame --exclude-module nltk --exclude-module spacy --exclude-module yt_dlp --exclude-module transformers --exclude-module boto3 --exclude-module botocore --exclude-module grpc --exclude-module onnxruntime --exclude-module opentelemetry --exclude-module timm --exclude-module emoji --exclude-module pygments --exclude-module jinja2 --exclude-module anyio --exclude-module orjson --exclude-module uvicorn --exclude-module fsspec --exclude-module websockets --exclude-module psutil --exclude-module regex --name pomera pomera.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Build failed!"
    echo "Check the output above for error details"
    exit 1
fi

echo
echo "Build completed successfully!"
echo
echo "Executable location: dist/pomera/pomera"
echo
echo "To run the application:"
echo "  cd dist/pomera"
echo "  ./pomera"
echo

# Optional: Test the executable
read -p "Do you want to test the executable now? (y/n): " test
if [[ $test == "y" || $test == "Y" ]]; then
    echo
    echo "Testing executable..."
    cd dist/pomera
    ./pomera &
    cd ../..
fi

echo
echo "Build process complete!"