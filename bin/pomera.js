#!/usr/bin/env node

/**
 * Pomera AI Commander - GUI launcher
 * 
 * This script launches the Pomera GUI application.
 */

const { spawn } = require('child_process');
const path = require('path');

// Get the path to pomera.py
const pomeraPath = path.join(__dirname, '..', 'pomera.py');

// Find Python executable
function findPython() {
    const { execSync } = require('child_process');

    // Try pythonw first (Windows - no console)
    if (process.platform === 'win32') {
        try {
            execSync('pythonw --version', { stdio: 'ignore' });
            return 'pythonw';
        } catch (e) {
            // Fall through
        }
    }

    // Try python3 (Linux/macOS)
    try {
        execSync('python3 --version', { stdio: 'ignore' });
        return 'python3';
    } catch (e) {
        // Fall back to python
        try {
            execSync('python --version', { stdio: 'ignore' });
            return 'python';
        } catch (e) {
            console.error('Error: Python is not installed or not in PATH');
            console.error('Please install Python 3.8 or higher');
            process.exit(1);
        }
    }
}

const pythonCmd = findPython();

// Spawn the Python GUI
const app = spawn(pythonCmd, [pomeraPath], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..'),
    detached: process.platform !== 'win32' // Detach on non-Windows
});

// Handle process exit
app.on('close', (code) => {
    process.exit(code || 0);
});

// Handle errors
app.on('error', (err) => {
    console.error('Failed to start Pomera:', err.message);
    process.exit(1);
});

// Forward signals
process.on('SIGINT', () => app.kill('SIGINT'));
process.on('SIGTERM', () => app.kill('SIGTERM'));
