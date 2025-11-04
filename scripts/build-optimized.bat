@echo off
echo Building OPTIMIZED Pomera AI Commander executable...
echo This build focuses on minimal size and maximum compression.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install minimal requirements
echo Installing minimal requirements...
pip install -r scripts/requirements-minimal.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building with maximum optimization...
echo This may take a few minutes...

python -m PyInstaller --onefile --windowed ^
    --optimize 2 ^
    --strip ^
    --noupx ^
    --exclude-module pytest --exclude-module test --exclude-module tests ^
    --exclude-module matplotlib --exclude-module scipy --exclude-module pandas ^
    --exclude-module jupyter --exclude-module IPython ^
    --exclude-module torch --exclude-module torchvision --exclude-module torchaudio ^
    --exclude-module tensorflow --exclude-module sklearn --exclude-module cv2 ^
    --exclude-module numpy --exclude-module pygame --exclude-module nltk ^
    --exclude-module spacy --exclude-module yt_dlp --exclude-module transformers ^
    --exclude-module boto3 --exclude-module botocore --exclude-module grpc ^
    --exclude-module onnxruntime --exclude-module opentelemetry --exclude-module timm ^
    --exclude-module emoji --exclude-module pygments --exclude-module jinja2 ^
    --exclude-module anyio --exclude-module orjson --exclude-module uvicorn ^
    --exclude-module fsspec --exclude-module websockets --exclude-module psutil ^
    --exclude-module regex --exclude-module pydantic --exclude-module dateutil ^
    --exclude-module pytz ^
    --exclude-module six --exclude-module pkg_resources ^
    --name pomera-optimized pomera.py

if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Checking for UPX compression...
upx --version >nul 2>&1
if errorlevel 1 (
    echo UPX not found. Install UPX for additional 50-70%% size reduction:
    echo https://upx.github.io/
    echo.
    goto :skip_upx
)

echo Compressing with UPX...
echo This will take a moment...
upx --best --lzma dist\pomera-optimized.exe
if errorlevel 1 (
    echo UPX compression failed, but executable is still usable
) else (
    echo UPX compression successful!
)

:skip_upx
echo.
echo Build completed!
echo.
if exist "dist\pomera-optimized.exe" (
    echo Executable: dist\pomera-optimized.exe
    for %%I in ("dist\pomera-optimized.exe") do echo Size: %%~zI bytes
    echo.
    set /p test="Test the executable now? (y/n): "
    if /i "!test!"=="y" (
        start dist\pomera-optimized.exe
    )
) else (
    echo ERROR: Executable not found!
)

pause