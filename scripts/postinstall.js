#!/usr/bin/env node
/**
 * Pomera AI Commander - npm postinstall script
 * 
 * This script runs after npm install/update and checks for
 * databases in the package directory that might be at risk.
 * 
 * Displays a warning if portable mode data is detected.
 */

const fs = require('fs');
const path = require('path');

// Package root directory
const packageDir = path.join(__dirname, '..');

// Check for databases in package directory
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

// If databases found in package directory, show warning
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
    // No databases in package directory - safe configuration
    console.log('✅ Pomera AI Commander installed successfully.');
    console.log('   Data will be stored in platform-appropriate directory (safe from updates).');
}
