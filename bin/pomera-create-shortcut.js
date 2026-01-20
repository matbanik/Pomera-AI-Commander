#!/usr/bin/env node

/**
 * Pomera AI Commander - Desktop Shortcut Creator
 * 
 * This script creates a desktop shortcut for the Pomera GUI.
 */

const { spawn } = require('child_process');
const path = require('path');

// Get the path to create_shortcut.py
const shortcutScript = path.join(__dirname, '..', 'create_shortcut.py');

// Find Python executable
function findPython() {
    const { execSync } = require('child_process');

    try {
        execSync('python3 --version', { stdio: 'ignore' });
        return 'python3';
    } catch (e) {
        try {
            execSync('python --version', { stdio: 'ignore' });
            return 'python';
        } catch (e) {
            console.error('Error: Python is not installed or not in PATH');
            process.exit(1);
        }
    }
}

const pythonCmd = findPython();

// Get command line arguments
const args = process.argv.slice(2);

// Spawn the Python script
const proc = spawn(pythonCmd, [shortcutScript, ...args], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
});

proc.on('close', (code) => {
    process.exit(code || 0);
});

proc.on('error', (err) => {
    console.error('Failed to create shortcut:', err.message);
    process.exit(1);
});
