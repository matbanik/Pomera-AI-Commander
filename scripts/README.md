# Build Scripts and Tools

This directory contains all build scripts, Docker files, and build-related tools for Pomera AI Commander.

## Build Scripts

### Local Builds
- `build.bat` / `build.sh` - Standard local build (onedir)
- `build-optimized.bat` - Optimized build with maximum size reduction
- `build-all.bat` - Interactive menu for all build types

### Docker Builds
- `build-docker.bat` / `build-docker.sh` - Simple Docker Linux build
- `docker-compose.yml` - Multi-variant Docker builds

## Docker Files
- `Dockerfile.linux` - Basic Linux build (Python slim)
- `Dockerfile.ubuntu` - Ubuntu-based build (high compatibility)
- `Dockerfile.alpine` - Alpine-based build (smaller size)

## Configuration Files
- `requirements-minimal.txt` - Minimal dependencies for optimized builds

## Testing and Validation
- `validate-release-workflow.py` - Release workflow validation script
- `test-linux-simple.bat` - Simple Linux testing script

## Usage

### Quick Start
```bash
# Windows - Standard build
scripts\build.bat

# Windows - Optimized build
scripts\build-optimized.bat

# Linux/macOS - Standard build
chmod +x scripts/build.sh
./scripts/build.sh

# Docker build (any platform)
./scripts/build-docker.sh
```

### Docker Multi-Platform
```bash
cd scripts
docker-compose up build-ubuntu    # Ubuntu variant
docker-compose up build-alpine    # Alpine variant
```

See the main [BUILD.md](../BUILD.md) for detailed documentation.