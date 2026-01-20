#!/usr/bin/env node
/**
 * Pomera AI Commander - npm postinstall script
 * 
 * This script runs after npm install/update and:
 * 1. Checks for databases in the package directory that might be at risk
 * 2. Creates a desktop shortcut for easy access to the GUI
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const os = require('os');

// Package root directory
const packageDir = path.join(__dirname, '..');

// ============================================================
// Part 1: Database Warning Check
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
} else {
    console.log('✅ Pomera AI Commander installed successfully.');
    console.log('   Data will be stored in platform-appropriate directory (safe from updates).');
}

// ============================================================
// Part 2: Desktop Shortcut Creation
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
        psScript += `$Shortcut.IconLocation = "${iconPath.replace(/\\/g, '\\\\')},0"\n`;
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

    const script = `#!/bin/bash
# Pomera AI Commander Launcher
cd "${packageDir}"
python3 "${pomeraPath}"
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

    const icon = fs.existsSync(iconPath) ? iconPath : 'utilities-terminal';

    const desktopEntry = `[Desktop Entry]
Version=1.0
Type=Application
Name=Pomera AI Commander
Comment=Text Processing Toolkit with MCP tools for AI assistants
Exec=python3 "${pomeraPath}"
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

// Check if Python/pythonw is available before creating shortcut
function checkPython() {
    try {
        if (process.platform === 'win32') {
            execSync('where pythonw', { stdio: 'pipe' });
        } else {
            execSync('which python3', { stdio: 'pipe' });
        }
        return true;
    } catch (e) {
        return false;
    }
}

// Create shortcut if Python is available
if (checkPython()) {
    createDesktopShortcut();
} else {
    console.log('\n⚠️  Python not found in PATH. Desktop shortcut not created.');
    console.log('   Install Python and run: python create_shortcut.py');
}

console.log('\n📖 To start the GUI manually:');
console.log('   python pomera.py');
console.log('\n📖 To start the MCP server:');
console.log('   npx pomera-ai-commander');
console.log('');

