@echo off
echo Building Linux executable using Docker...
echo.

REM Check if Docker is installed and running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

REM Create output directory
if not exist "dist-docker" mkdir dist-docker

echo Building Docker image...
docker build -f scripts/Dockerfile.linux -t pomera-linux-builder .

if errorlevel 1 (
    echo ERROR: Failed to build Docker image
    pause
    exit /b 1
)

echo.
echo Running Docker container to build Linux executable...
docker run --rm -v "%cd%\dist-docker:/host-output" pomera-linux-builder

if errorlevel 1 (
    echo ERROR: Failed to build Linux executable
    pause
    exit /b 1
)

echo.
echo Linux executable built successfully!
echo Location: dist-docker\pomera-linux
echo.

REM Check if file was created
if exist "dist-docker\pomera-linux" (
    echo File size:
    dir "dist-docker\pomera-linux" | find "pomera-linux"
    echo.
    echo You can now test this executable on a Linux system.
) else (
    echo ERROR: Executable was not created
)

echo.
echo Build complete!
pause