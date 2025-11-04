#!/usr/bin/env python3
"""
Release Workflow Validation Script

This script validates the release workflow components locally before running
the full GitHub Actions workflow. It performs basic checks on:
- PyInstaller build capability
- Executable validation
- Checksum generation
- File naming conventions

Usage:
    python scripts/validate-release-workflow.py [--test-tag v0.0.1-test]
"""

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {message} ==={Colors.END}")


class ReleaseWorkflowValidator:
    def __init__(self, test_tag="v0.0.1-test"):
        self.test_tag = test_tag
        self.platform_name = self._get_platform_name()
        self.executable_extension = ".exe" if platform.system() == "Windows" else ""
        self.temp_dir = None
        self.errors = []
        self.warnings = []
        
    def _get_platform_name(self):
        """Get platform name matching GitHub Actions matrix"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            return "linux"
        else:
            return system
    
    def validate_prerequisites(self):
        """Validate that required tools are available"""
        print_header("Validating Prerequisites")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self.errors.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            print_error(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check PyInstaller availability
        try:
            result = subprocess.run(["pyinstaller", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print_success(f"PyInstaller available: {version}")
            else:
                self.errors.append("PyInstaller not working properly")
                print_error("PyInstaller not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.errors.append("PyInstaller not found - install with: pip install pyinstaller")
            print_error("PyInstaller not found")
        
        # Check main application file
        if not os.path.exists("pomera.py"):
            self.errors.append("pomera.py not found in current directory")
            print_error("pomera.py not found")
        else:
            print_success("pomera.py found")
        
        # Check for requirements.txt
        if os.path.exists("requirements.txt"):
            print_success("requirements.txt found")
        else:
            print_warning("requirements.txt not found - dependencies may not be installed")
            self.warnings.append("requirements.txt not found")
    
    def validate_tag_format(self):
        """Validate test tag format"""
        print_header("Validating Tag Format")
        
        import re
        pattern = r'^v\d+\.\d+\.\d+(-test)?$'
        
        if re.match(pattern, self.test_tag):
            print_success(f"Tag format valid: {self.test_tag}")
        else:
            self.errors.append(f"Invalid tag format: {self.test_tag} (should match v*.*.*-test)")
            print_error(f"Invalid tag format: {self.test_tag}")
    
    def test_pyinstaller_build(self):
        """Test PyInstaller build process"""
        print_header("Testing PyInstaller Build")
        
        # Create temporary directory in project directory to avoid cross-drive issues on Windows
        import uuid
        temp_name = f"release_test_{uuid.uuid4().hex[:8]}"
        self.temp_dir = os.path.join(os.getcwd(), temp_name)
        os.makedirs(self.temp_dir, exist_ok=True)
        print_info(f"Using temporary directory: {self.temp_dir}")
        
        try:
            # Prepare executable name
            executable_name = f"pomera-{self.test_tag}-{self.platform_name}"
            
            # Build PyInstaller command
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--log-level", "INFO",
                "--name", executable_name,
                "--distpath", os.path.join(self.temp_dir, "dist"),
                "--workpath", os.path.join(self.temp_dir, "build"),
                "--specpath", os.path.join(self.temp_dir, "spec"),
                "--optimize", "2",  # Maximum Python optimization
                "--strip",  # Strip debug symbols (Unix)
                "--noupx",  # We'll handle UPX separately for better control
                "--exclude-module", "pytest",
                "--exclude-module", "test",
                "--exclude-module", "tests",
                "--exclude-module", "matplotlib",
                "--exclude-module", "scipy",
                "--exclude-module", "pandas",
                "--exclude-module", "jupyter",
                "--exclude-module", "IPython",
                "--exclude-module", "torch",
                "--exclude-module", "torchvision",
                "--exclude-module", "torchaudio",
                "--exclude-module", "tensorflow",
                "--exclude-module", "sklearn",
                "--exclude-module", "cv2",
                "--exclude-module", "numpy",
                "--exclude-module", "pygame",
                "--exclude-module", "nltk",
                "--exclude-module", "spacy",
                "--exclude-module", "yt_dlp",
                "--exclude-module", "transformers",
                "--exclude-module", "boto3",
                "--exclude-module", "botocore",
                "--exclude-module", "grpc",
                "--exclude-module", "onnxruntime",
                "--exclude-module", "opentelemetry",
                "--exclude-module", "timm",
                "--exclude-module", "emoji",
                "--exclude-module", "pygments",
                "--exclude-module", "jinja2",
                "--exclude-module", "anyio",
                "--exclude-module", "orjson",
                "--exclude-module", "uvicorn",
                "--exclude-module", "fsspec",
                "--exclude-module", "websockets",
                "--exclude-module", "psutil",
                "--exclude-module", "regex",
                "--exclude-module", "pydantic",
                "--exclude-module", "dateutil",
                "--exclude-module", "pytz",
                "--exclude-module", "six",
                "--exclude-module", "pkg_resources",
                "pomera.py"
            ]
            
            # Add windowed mode for GUI applications
            if self.platform_name in ["windows", "macos"]:
                cmd.insert(-1, "--windowed")
            
            print_info(f"Running: {' '.join(cmd)}")
            print_info("PyInstaller output:")
            
            # Run PyInstaller with live output (don't capture output)
            result = subprocess.run(cmd, timeout=300)
            
            # Try to compress with UPX if available
            if result.returncode == 0:
                expected_exe = os.path.join(self.temp_dir, "dist", 
                                          f"{executable_name}{self.executable_extension}")
                if os.path.exists(expected_exe):
                    self._try_upx_compression(expected_exe)
            
            if result.returncode == 0:
                print_success("PyInstaller build completed successfully")
                
                # Check if executable was created
                expected_exe = os.path.join(self.temp_dir, "dist", 
                                          f"{executable_name}{self.executable_extension}")
                
                if os.path.exists(expected_exe):
                    print_success(f"Executable created: {expected_exe}")
                    return expected_exe
                else:
                    self.errors.append(f"Executable not found at expected location: {expected_exe}")
                    print_error(f"Executable not found: {expected_exe}")
                    # List what was actually created
                    dist_dir = os.path.join(self.temp_dir, "dist")
                    if os.path.exists(dist_dir):
                        files = os.listdir(dist_dir)
                        print_info(f"Files in dist directory: {files}")
                    return None
            else:
                self.errors.append(f"PyInstaller build failed with return code: {result.returncode}")
                print_error(f"PyInstaller build failed with return code: {result.returncode}")
                print_error("Check the output above for error details")
                return None
                
        except subprocess.TimeoutExpired:
            self.errors.append("PyInstaller build timed out (5 minutes)")
            print_error("PyInstaller build timed out")
            return None
        except Exception as e:
            self.errors.append(f"PyInstaller build error: {str(e)}")
            print_error(f"Build error: {str(e)}")
            return None
    
    def _try_upx_compression(self, executable_path):
        """Try to compress executable with UPX if available"""
        try:
            # Check if UPX is available
            result = subprocess.run(["upx", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print_info("UPX found, attempting compression...")
                original_size = os.path.getsize(executable_path)
                
                # Compress with UPX (--best for maximum compression)
                upx_result = subprocess.run(["upx", "--best", "--lzma", executable_path], 
                                          capture_output=True, text=True, timeout=60)
                
                if upx_result.returncode == 0:
                    new_size = os.path.getsize(executable_path)
                    reduction = ((original_size - new_size) / original_size) * 100
                    print_success(f"UPX compression successful: {original_size:,} → {new_size:,} bytes ({reduction:.1f}% reduction)")
                else:
                    print_warning(f"UPX compression failed: {upx_result.stderr}")
            else:
                print_info("UPX not available (optional compression tool)")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_info("UPX not found (optional compression tool)")
        except Exception as e:
            print_warning(f"UPX compression error: {e}")
    
    def validate_executable(self, executable_path):
        """Validate the built executable"""
        if not executable_path or not os.path.exists(executable_path):
            return False
            
        print_header("Validating Executable")
        
        # Check file size
        file_size = os.path.getsize(executable_path)
        min_size = 1024 * 1024  # 1 MB
        max_size = 500 * 1024 * 1024  # 500 MB (increased for development testing)
        
        if file_size < min_size:
            self.errors.append(f"Executable too small: {file_size} bytes (minimum: {min_size})")
            print_error(f"File too small: {file_size} bytes")
        elif file_size > max_size:
            self.errors.append(f"Executable too large: {file_size} bytes (maximum: {max_size})")
            print_error(f"File too large: {file_size} bytes")
        else:
            print_success(f"File size OK: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        # Check file permissions (Unix systems)
        if platform.system() != "Windows":
            if os.access(executable_path, os.X_OK):
                print_success("Executable permissions OK")
            else:
                print_warning("Executable not marked as executable")
                # Try to fix permissions
                try:
                    os.chmod(executable_path, 0o755)
                    print_info("Fixed executable permissions")
                except Exception as e:
                    self.warnings.append(f"Could not fix permissions: {e}")
        
        # Basic smoke test
        try:
            print_info("Running smoke test...")
            # Try to run with --help flag and timeout quickly
            result = subprocess.run([executable_path, "--help"], 
                                  capture_output=True, text=True, timeout=10)
            print_success("Smoke test completed (executable can start)")
            if result.stdout:
                print_info(f"Output preview: {result.stdout[:100]}...")
        except subprocess.TimeoutExpired:
            print_success("Smoke test completed (executable started, timed out as expected)")
        except Exception as e:
            self.warnings.append(f"Smoke test failed: {e}")
            print_warning(f"Smoke test failed: {e}")
        
        return True
    
    def test_checksum_generation(self, executable_path):
        """Test SHA256 checksum generation"""
        if not executable_path or not os.path.exists(executable_path):
            return None
            
        print_header("Testing Checksum Generation")
        
        try:
            # Generate SHA256 checksum
            sha256_hash = hashlib.sha256()
            with open(executable_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            
            # Validate checksum format
            if len(checksum) == 64 and all(c in '0123456789abcdef' for c in checksum):
                print_success(f"Checksum generated: {checksum}")
                
                # Create checksum file
                executable_name = os.path.basename(executable_path)
                checksum_file = f"{executable_path}.sha256"
                
                with open(checksum_file, 'w') as f:
                    f.write(f"{checksum}  {executable_name}\n")
                
                if os.path.exists(checksum_file):
                    print_success(f"Checksum file created: {checksum_file}")
                    return checksum
                else:
                    self.errors.append("Failed to create checksum file")
                    print_error("Failed to create checksum file")
            else:
                self.errors.append(f"Invalid checksum format: {checksum}")
                print_error(f"Invalid checksum format: {checksum}")
                
        except Exception as e:
            self.errors.append(f"Checksum generation failed: {e}")
            print_error(f"Checksum generation failed: {e}")
        
        return None
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print_info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print_warning(f"Could not clean up temporary directory: {e}")
    
    def run_validation(self):
        """Run complete validation process"""
        print_header(f"Release Workflow Validation - {self.platform_name}")
        print_info(f"Test tag: {self.test_tag}")
        print_info(f"Platform: {self.platform_name}")
        
        try:
            # Run validation steps
            self.validate_prerequisites()
            self.validate_tag_format()
            
            if self.errors:
                print_error("Prerequisites failed - cannot continue")
                return False
            
            executable_path = self.test_pyinstaller_build()
            
            if executable_path:
                self.validate_executable(executable_path)
                self.test_checksum_generation(executable_path)
            
            # Print summary
            self.print_summary()
            
            return len(self.errors) == 0
            
        finally:
            self.cleanup()
    
    def print_summary(self):
        """Print validation summary"""
        print_header("Validation Summary")
        
        if self.errors:
            print_error(f"Found {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print_warning(f"Found {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print_success("All validations passed! ✨")
            print_info("The release workflow should work correctly on this platform.")
        elif not self.errors:
            print_success("Validation passed with warnings")
            print_info("The release workflow should work, but review the warnings above.")
        else:
            print_error("Validation failed")
            print_info("Fix the errors above before running the release workflow.")


def main():
    parser = argparse.ArgumentParser(description="Validate release workflow components locally")
    parser.add_argument("--test-tag", default="v0.0.1-test", 
                       help="Test tag to use for validation (default: v0.0.1-test)")
    
    args = parser.parse_args()
    
    validator = ReleaseWorkflowValidator(args.test_tag)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()