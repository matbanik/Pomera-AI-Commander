#!/usr/bin/env node
/**
 * Pomera AI Commander - npm postinstall script
 * 
 * This script runs after npm install/update and:
 * 1. Creates a Python virtual environment with dependencies (for macOS/Linux PEP 668 compatibility)
 * 2. Checks for databases in the package directory that might be at risk
 * 3. Creates a desktop shortcut for easy access to the GUI
 * 
 * AI AGENTS: If user requests npm or PyPI install, this script should be run automatically.
 * For manual invocation: node scripts/postinstall.js
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawnSync } = require('child_process');
const os = require('os');

// Package root directory
const packageDir = path.join(__dirname, '..');

// ============================================================
// Part 1: Python Virtual Environment Setup
// ============================================================

function findSystemPython() {
    const pythonCmds = process.platform === 'win32'
        ? ['python', 'python3']
        : ['python3', 'python'];

    for (const cmd of pythonCmds) {
        try {
            execSync(`${cmd} --version`, { stdio: 'ignore' });
            return cmd;
        } catch (e) {
            // Continue to next
        }
    }
    return null;
}

function installPythonDeps() {
    const isWin = process.platform === 'win32';
    const venvDir = path.join(packageDir, '.venv');
    const requirementsPath = path.join(packageDir, 'requirements.txt');

    // Platform-specific paths within venv
    const venvPython = path.join(venvDir,
        isWin ? 'Scripts' : 'bin',
        isWin ? 'python.exe' : 'python3');
    const venvPip = path.join(venvDir,
        isWin ? 'Scripts' : 'bin',
        isWin ? 'pip.exe' : 'pip');

    // Skip if venv already exists and has pip
    if (fs.existsSync(venvPython) && fs.existsSync(venvPip)) {
        console.log('✓ Python virtual environment already exists');
        return true;
    }

    // Find system Python
    const systemPython = findSystemPython();
    if (!systemPython) {
        console.log('\n⚠️  Python not found. Please install Python 3.8+ and run:');
        console.log('   node scripts/postinstall.js');
        console.log('   Or manually: pip3 install -r requirements.txt\n');
        return false;
    }

    console.log('\n📦 Creating Python virtual environment...');
    console.log(`   Using: ${systemPython}`);

    try {
        // Create venv
        const createResult = spawnSync(systemPython, ['-m', 'venv', venvDir], {
            stdio: 'inherit',
            cwd: packageDir
        });

        if (createResult.status !== 0) {
            throw new Error('Failed to create venv');
        }

        // Check if requirements.txt exists
        if (!fs.existsSync(requirementsPath)) {
            console.log('⚠️  requirements.txt not found, skipping dependency installation');
            return true;
        }

        // Upgrade pip (optional but recommended)
        console.log('📦 Upgrading pip...');
        spawnSync(venvPython, ['-m', 'pip', 'install', '--upgrade', 'pip'], {
            stdio: 'pipe',
            cwd: packageDir
        });

        // Install requirements
        console.log('📦 Installing Python dependencies (this may take a minute)...');
        const installResult = spawnSync(venvPip, ['install', '-r', requirementsPath], {
            stdio: 'inherit',
            cwd: packageDir
        });

        if (installResult.status !== 0) {
            throw new Error('Failed to install requirements');
        }

        console.log('✅ Python dependencies installed successfully!\n');
        return true;

    } catch (err) {
        console.error('\n❌ Failed to set up Python environment:', err.message);
        console.log('\n📋 Manual installation options:');
        console.log('   Option 1 (Recommended): Create venv manually:');
        console.log(`      cd "${packageDir}"`);
        console.log('      python3 -m venv .venv');
        console.log('      .venv/bin/pip install -r requirements.txt  # macOS/Linux');
        console.log('      .venv\\Scripts\\pip install -r requirements.txt  # Windows');
        console.log('\n   Option 2: Install globally (may require --break-system-packages on macOS):');
        console.log('      pip3 install --break-system-packages -r requirements.txt\n');
        return false;
    }
}

// Run Python setup first
const pythonOk = installPythonDeps();

// ============================================================
// Part 2: Database Warning Check
// ============================================================

const databases = ['settings.db', 'notes.db', 'settings.json'];
const foundDatabases = [];

databases.forEach(db => {
    const dbPath = path.join(packageDir, db);
    if (fs.existsSync(dbPath)) {
        const stats = fs.statSync(dbPath);
        foundDatabases.push({
            name: db,
            path: dbPath,
            size: stats.size
        });
    }
});

if (foundDatabases.length > 0) {
    console.log('\n' + '='.repeat(70));
    console.log('⚠️  POMERA DATA WARNING ⚠️');
    console.log('='.repeat(70));
    console.log('\nData files detected in package directory (portable mode):');
    foundDatabases.forEach(db => {
        console.log(`  • ${db.name} (${(db.size / 1024).toFixed(1)} KB)`);
    });
    console.log('\n🚨 IMPORTANT:');
    console.log('   These files WILL BE DELETED if you run "npm update"!');
    console.log('\n📋 BEFORE UPDATING, please:');
    console.log('   1. Export your settings: Help > Export Settings');
    console.log('   2. Copy database files to a safe location:');
    console.log(`      ${packageDir}`);
    console.log('\n💡 RECOMMENDED: Use platform data directories instead of portable mode.');
    console.log('   Run Pomera without --portable flag to store data in:');
    if (process.platform === 'win32') {
        console.log('   %LOCALAPPDATA%\\PomeraAI\\Pomera-AI-Commander\\');
    } else if (process.platform === 'darwin') {
        console.log('   ~/Library/Application Support/Pomera-AI-Commander/');
    } else {
        console.log('   ~/.local/share/Pomera-AI-Commander/');
    }
    console.log('\n' + '='.repeat(70) + '\n');
} else if (pythonOk) {
    console.log('✅ Pomera AI Commander installed successfully.');
    console.log('   Data will be stored in platform-appropriate directory (safe from updates).');
}

// ============================================================
// Part 3: Desktop Shortcut Creation
// ============================================================

function getDesktopPath() {
    if (process.platform === 'win32') {
        return path.join(os.homedir(), 'Desktop');
    } else if (process.platform === 'darwin') {
        return path.join(os.homedir(), 'Desktop');
    } else {
        // Linux - check XDG
        const xdgDesktop = process.env.XDG_DESKTOP_DIR;
        if (xdgDesktop) return xdgDesktop;
        return path.join(os.homedir(), 'Desktop');
    }
}

function createWindowsShortcut() {
    const desktop = getDesktopPath();
    const shortcutPath = path.join(desktop, 'Pomera AI Commander.lnk');
    const pomeraPath = path.join(packageDir, 'pomera.py');
    const iconPath = path.join(packageDir, 'resources', 'icon.ico');

    let psScript = `
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("${shortcutPath.replace(/\\/g, '\\\\')}")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = '"${pomeraPath.replace(/\\/g, '\\\\')}"'
$Shortcut.WorkingDirectory = "${packageDir.replace(/\\/g, '\\\\')}"
$Shortcut.Description = "Pomera AI Commander - Text Processing Toolkit"
`;
    if (fs.existsSync(iconPath)) {
        psScript += `$Shortcut.IconLocation = "${iconPath.replace(/\\/g, '\\\\')}",0\n`;
    }
    psScript += '$Shortcut.Save()';

    try {
        execSync(`powershell -Command "${psScript.replace(/"/g, '\\"')}"`, { stdio: 'pipe' });
        console.log(`\n🐕 Desktop shortcut created: ${shortcutPath}`);
        return true;
    } catch (e) {
        console.log('\n⚠️  Could not create desktop shortcut automatically.');
        console.log('   Run: python create_shortcut.py');
        return false;
    }
}

function createMacOSShortcut() {
    const desktop = getDesktopPath();
    const shortcutPath = path.join(desktop, 'Pomera AI Commander.command');
    const pomeraPath = path.join(packageDir, 'pomera.py');
    const venvPython = path.join(packageDir, '.venv', 'bin', 'python3');

    // Use venv Python if available, otherwise system python3
    const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python3';

    const script = `#!/bin/bash
# Pomera AI Commander Launcher
cd "${packageDir}"
"${pythonCmd}" "${pomeraPath}"
`;

    try {
        fs.writeFileSync(shortcutPath, script);
        fs.chmodSync(shortcutPath, 0o755);
        console.log(`\n🐕 Desktop launcher created: ${shortcutPath}`);
        return true;
    } catch (e) {
        console.log('\n⚠️  Could not create desktop shortcut automatically.');
        return false;
    }
}

function createLinuxShortcut() {
    const desktop = getDesktopPath();
    const shortcutPath = path.join(desktop, 'pomera-ai-commander.desktop');
    const pomeraPath = path.join(packageDir, 'pomera.py');
    const iconPath = path.join(packageDir, 'resources', 'icon.png');
    const venvPython = path.join(packageDir, '.venv', 'bin', 'python3');

    const icon = fs.existsSync(iconPath) ? iconPath : 'utilities-terminal';
    // Use venv Python if available
    const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python3';

    const desktopEntry = `[Desktop Entry]
Version=1.0
Type=Application
Name=Pomera AI Commander
Comment=Text Processing Toolkit with MCP tools for AI assistants
Exec="${pythonCmd}" "${pomeraPath}"
Icon=${icon}
Terminal=false
Categories=Development;Utility;TextTools;
StartupNotify=true
`;

    try {
        fs.writeFileSync(shortcutPath, desktopEntry);
        fs.chmodSync(shortcutPath, 0o755);
        console.log(`\n🐕 Desktop launcher created: ${shortcutPath}`);

        // Also add to applications menu
        const appsDir = path.join(os.homedir(), '.local', 'share', 'applications');
        if (!fs.existsSync(appsDir)) {
            fs.mkdirSync(appsDir, { recursive: true });
        }
        const appsPath = path.join(appsDir, 'pomera-ai-commander.desktop');
        fs.writeFileSync(appsPath, desktopEntry);
        console.log(`   Also added to applications menu`);

        return true;
    } catch (e) {
        console.log('\n⚠️  Could not create desktop shortcut automatically.');
        return false;
    }
}

function createDesktopShortcut() {
    console.log('\n🐕 Creating desktop shortcut...');

    const desktop = getDesktopPath();
    if (!fs.existsSync(desktop)) {
        console.log(`   Desktop directory not found: ${desktop}`);
        return false;
    }

    if (process.platform === 'win32') {
        return createWindowsShortcut();
    } else if (process.platform === 'darwin') {
        return createMacOSShortcut();
    } else {
        return createLinuxShortcut();
    }
}

// Check if Python is available before creating shortcut
function checkPython() {
    return pythonOk || findSystemPython() !== null;
}

// Create shortcut if Python is available
if (checkPython()) {
    createDesktopShortcut();
} else {
    console.log('\n⚠️  Python not found in PATH. Desktop shortcut not created.');
    console.log('   Install Python and run: python create_shortcut.py');
}

console.log('\n📖 To start the GUI manually:');
console.log('   pomera');
console.log('\n📖 To start the MCP server:');
console.log('   pomera-mcp');
console.log('');
