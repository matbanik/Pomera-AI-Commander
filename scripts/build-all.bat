@echo off
echo Pomera AI Commander - Multi-Platform Build Script
echo ==================================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
set DOCKER_AVAILABLE=%errorlevel%

echo Available build options:
echo 1. Windows (local PyInstaller)
echo 2. Linux (Docker - Ubuntu base)
echo 3. Linux (Docker - Alpine base - smaller)
echo 4. All platforms (Windows local + Linux Docker)
if %DOCKER_AVAILABLE% neq 0 echo    Note: Docker not available - Linux builds disabled
echo 5. Exit
echo.

set /p choice="Select build option (1-5): "

if "%choice%"=="1" goto build_windows
if "%choice%"=="2" goto build_linux_ubuntu
if "%choice%"=="3" goto build_linux_alpine
if "%choice%"=="4" goto build_all
if "%choice%"=="5" goto exit
goto invalid_choice

:build_windows
echo.
echo Building Windows executable...
call build.bat
goto end

:build_linux_ubuntu
if %DOCKER_AVAILABLE% neq 0 goto no_docker
echo.
echo Building Linux executable (Ubuntu base)...
docker build -f scripts/Dockerfile.ubuntu -t pomera-ubuntu-builder .
if errorlevel 1 goto docker_error
mkdir dist-docker 2>nul
docker run --rm -v "%cd%\dist-docker:/output" pomera-ubuntu-builder
echo Linux executable: dist-docker\pomera-linux-ubuntu
goto end

:build_linux_alpine
if %DOCKER_AVAILABLE% neq 0 goto no_docker
echo.
echo Building Linux executable (Alpine base - smaller)...
docker build -f scripts/Dockerfile.alpine -t pomera-alpine-builder .
if errorlevel 1 goto docker_error
mkdir dist-docker 2>nul
docker run --rm -v "%cd%\dist-docker:/output" pomera-alpine-builder
echo Linux executable: dist-docker\pomera-linux-alpine
goto end

:build_all
echo.
echo Building all platforms...
echo.
echo [1/3] Building Windows executable...
call build.bat
if errorlevel 1 goto error

if %DOCKER_AVAILABLE% neq 0 (
    echo Docker not available - skipping Linux builds
    goto end
)

echo.
echo [2/3] Building Linux executable (Ubuntu)...
docker build -f scripts/Dockerfile.ubuntu -t pomera-ubuntu-builder .
if errorlevel 1 goto docker_error
mkdir dist-docker 2>nul
docker run --rm -v "%cd%\dist-docker:/output" pomera-ubuntu-builder

echo.
echo [3/3] Building Linux executable (Alpine)...
docker build -f scripts/Dockerfile.alpine -t pomera-alpine-builder .
if errorlevel 1 goto docker_error
docker run --rm -v "%cd%\dist-docker:/output" pomera-alpine-builder

echo.
echo All builds completed!
echo Windows: dist\pomera\pomera.exe
echo Linux (Ubuntu): dist-docker\pomera-linux-ubuntu
echo Linux (Alpine): dist-docker\pomera-linux-alpine
goto end

:no_docker
echo ERROR: Docker is not available
echo Please install Docker Desktop to build Linux executables
goto end

:docker_error
echo ERROR: Docker build failed
echo Check the output above for details
goto end

:invalid_choice
echo Invalid choice. Please select 1-5.
goto end

:error
echo Build failed!
goto end

:exit
echo Exiting...
goto end

:end
echo.
pause