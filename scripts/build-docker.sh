#!/bin/bash

echo "Building Linux executable using Docker..."
echo

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker and try again"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Create output directory
mkdir -p dist-docker

echo "Building Docker image..."
docker build -f scripts/Dockerfile.linux -t pomera-linux-builder .

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build Docker image"
    exit 1
fi

echo
echo "Running Docker container to build Linux executable..."
docker run --rm -v "$(pwd)/dist-docker:/host-output" pomera-linux-builder

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build Linux executable"
    exit 1
fi

echo
echo "Linux executable built successfully!"
echo "Location: dist-docker/pomera-linux"
echo

# Check if file was created
if [ -f "dist-docker/pomera-linux" ]; then
    echo "File size: $(ls -lh dist-docker/pomera-linux | awk '{print $5}')"
    echo
    echo "You can now test this executable on a Linux system."
else
    echo "ERROR: Executable was not created"
fi

echo
echo "Build complete!"