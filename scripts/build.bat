@echo off
echo Building Pomera AI Commander with PyInstaller...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install requirements if requirements.txt exists
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable with PyInstaller...
echo Command: pyinstaller --onedir --windowed [with many exclusions] --name pomera pomera.py

pyinstaller --onedir --windowed --exclude-module pytest --exclude-module test --exclude-module tests --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module jupyter --exclude-module IPython --exclude-module torch --exclude-module torchvision --exclude-module torchaudio --exclude-module tensorflow --exclude-module sklearn --exclude-module cv2 --exclude-module numpy --exclude-module pygame --exclude-module nltk --exclude-module spacy --exclude-module yt_dlp --exclude-module transformers --exclude-module boto3 --exclude-module botocore --exclude-module grpc --exclude-module onnxruntime --exclude-module opentelemetry --exclude-module timm --exclude-module emoji --exclude-module pygments --exclude-module jinja2 --exclude-module anyio --exclude-module orjson --exclude-module uvicorn --exclude-module fsspec --exclude-module websockets --exclude-module psutil --exclude-module regex --name pomera pomera.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo.
echo Executable location: dist\pomera\pomera.exe
echo.
echo To run the application:
echo   cd dist\pomera
echo   pomera.exe
echo.

REM Optional: Test the executable
set /p test="Do you want to test the executable now? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Testing executable...
    cd dist\pomera
    start pomera.exe
    cd ..\..
)

echo.
echo Build process complete!
pause