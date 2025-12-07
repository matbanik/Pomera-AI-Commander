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

REM Install additional AI SDK dependencies (may fail gracefully)
echo Installing additional AI SDK dependencies...
pip install google-genai>=1.0.0 2>nul
pip install azure-ai-inference>=1.0.0b1 azure-core>=1.30.0 2>nul
pip install tenacity>=8.2.0 2>nul
pip install aiohttp>=3.9.0 2>nul
echo AI SDK dependencies installation completed.

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist releases rmdir /s /q releases

REM Create releases directory
mkdir releases

echo.
echo ========================================
echo Building ONEDIR deployment...
echo ========================================
echo Command: pyinstaller --onedir --windowed [with many exclusions] --name pomera-onedir pomera.py

python -m PyInstaller --onedir --windowed --exclude-module pytest --exclude-module test --exclude-module tests --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module jupyter --exclude-module IPython --exclude-module torch --exclude-module torchvision --exclude-module torchaudio --exclude-module tensorflow --exclude-module sklearn --exclude-module cv2 --exclude-module numpy --exclude-module pygame --exclude-module nltk --exclude-module spacy --exclude-module yt_dlp --exclude-module transformers --exclude-module boto3 --exclude-module botocore --exclude-module grpc --exclude-module onnxruntime --exclude-module opentelemetry --exclude-module timm --exclude-module emoji --exclude-module pygments --exclude-module jinja2 --exclude-module anyio --exclude-module orjson --exclude-module uvicorn --exclude-module fsspec --exclude-module websockets --exclude-module psutil --exclude-module regex --name pomera-onedir pomera.py

if errorlevel 1 (
    echo.
    echo ERROR: ONEDIR build failed!
    echo Check the output above for error details
    pause
    exit /b 1
)

echo.
echo ONEDIR build completed successfully!
echo Creating ZIP file for ONEDIR deployment...

REM Create ZIP for onedir deployment
powershell -command "Compress-Archive -Path 'dist\pomera-onedir' -DestinationPath 'releases\pomera-onedir.zip' -Force"

if errorlevel 1 (
    echo ERROR: Failed to create ONEDIR ZIP file
    pause
    exit /b 1
)

echo ONEDIR ZIP created: releases\pomera-onedir.zip

echo.
echo ========================================
echo Building ONEFILE deployment...
echo ========================================
echo Command: pyinstaller --onefile --windowed [with many exclusions] --name pomera-onefile pomera.py

python -m PyInstaller --onefile --windowed --exclude-module pytest --exclude-module test --exclude-module tests --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module jupyter --exclude-module IPython --exclude-module torch --exclude-module torchvision --exclude-module torchaudio --exclude-module tensorflow --exclude-module sklearn --exclude-module cv2 --exclude-module numpy --exclude-module pygame --exclude-module nltk --exclude-module spacy --exclude-module yt_dlp --exclude-module transformers --exclude-module boto3 --exclude-module botocore --exclude-module grpc --exclude-module onnxruntime --exclude-module opentelemetry --exclude-module timm --exclude-module emoji --exclude-module pygments --exclude-module jinja2 --exclude-module anyio --exclude-module orjson --exclude-module uvicorn --exclude-module fsspec --exclude-module websockets --exclude-module psutil --exclude-module regex --name pomera-onefile pomera.py

if errorlevel 1 (
    echo.
    echo ERROR: ONEFILE build failed!
    echo Check the output above for error details
    pause
    exit /b 1
)

echo.
echo ONEFILE build completed successfully!
echo Creating ZIP file for ONEFILE deployment...

REM Create ZIP for onefile deployment (create a folder first to maintain structure)
mkdir dist\pomera-onefile-package
copy dist\pomera-onefile.exe dist\pomera-onefile-package\
powershell -command "Compress-Archive -Path 'dist\pomera-onefile-package' -DestinationPath 'releases\pomera-onefile.zip' -Force"

if errorlevel 1 (
    echo ERROR: Failed to create ONEFILE ZIP file
    pause
    exit /b 1
)

echo ONEFILE ZIP created: releases\pomera-onefile.zip

echo.
echo ========================================
echo BUILD SUMMARY
echo ========================================
echo Both deployments completed successfully!
echo.
echo ONEDIR deployment: releases\pomera-onedir.zip
echo   - Contains: pomera-onedir folder with executable and dependencies
echo   - Faster startup, larger size
echo   - To run: Extract and run pomera-onedir.exe
echo.
echo ONEFILE deployment: releases\pomera-onefile.zip
echo   - Contains: Single executable file
echo   - Slower startup, smaller download
echo   - To run: Extract and run pomera-onefile.exe
echo.

REM Optional: Test one of the executables
set /p test="Do you want to test the ONEFILE executable now? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Testing ONEFILE executable...
    start dist\pomera-onefile.exe
)

echo.
echo Build process complete!
echo Check the 'releases' folder for your ZIP files.
pause