#!/usr/bin/env node

/**
 * Pomera AI Commander - npm CLI wrapper
 * 
 * This script wraps the Python MCP server for npm-based installation.
 * It spawns the Python server with proper stdio handling.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get the path to the Python server
const serverPath = path.join(__dirname, '..', 'pomera_mcp_server.py');

// Get command line arguments (skip node and script path)
const args = process.argv.slice(2);

// Check for bundled venv Python first, fall back to system Python
function findPython() {
    const { execSync } = require('child_process');
    const isWin = process.platform === 'win32';

    // Check for bundled venv first (created by postinstall)
    const venvPython = path.join(__dirname, '..', '.venv',
        isWin ? 'Scripts' : 'bin',
        isWin ? 'python.exe' : 'python3');

    if (fs.existsSync(venvPython)) {
        return venvPython;
    }

    // Fall back to system Python
    // Try python3 first (Linux/macOS)
    try {
        execSync('python3 --version', { stdio: 'ignore' });
        return 'python3';
    } catch (e) {
        // Fall back to python (Windows usually)
        try {
            execSync('python --version', { stdio: 'ignore' });
            return 'python';
        } catch (e) {
            console.error('Error: Python is not installed or not in PATH');
            console.error('Please install Python 3.8 or higher: https://www.python.org/downloads/');
            process.exit(1);
        }
    }
}

const pythonCmd = findPython();

// Spawn the Python server
const server = spawn(pythonCmd, [serverPath, ...args], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
});

// Handle process exit
server.on('close', (code) => {
    process.exit(code || 0);
});

// Handle errors
server.on('error', (err) => {
    console.error('Failed to start Pomera MCP server:', err.message);
    console.error('Make sure Python 3.8+ is installed and in your PATH');
    process.exit(1);
});

// Forward signals to child process
process.on('SIGINT', () => server.kill('SIGINT'));
process.on('SIGTERM', () => server.kill('SIGTERM'));
