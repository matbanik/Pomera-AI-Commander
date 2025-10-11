@echo off
echo Testing Linux executable in Docker container...
echo.

REM Check if the Linux executable exists
if not exist "dist-docker\pomera-linux" (
    echo ERROR: Linux executable not found!
    echo Please build it first using: build-docker.bat
    pause
    exit /b 1
)

echo Starting Ubuntu container with your Linux executable...
echo.
echo Commands you can try inside the container:
echo   ./pomera-linux --help
echo   ./pomera-linux --version
echo   ls -la pomera-linux
echo   file pomera-linux
echo.
echo Type 'exit' to return to Windows
echo.

docker run -it --rm -v "%cd%\dist-docker:/app" -w /app ubuntu:22.04 /bin/bash

echo.
echo Returned to Windows
pause