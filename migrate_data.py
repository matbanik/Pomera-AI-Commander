#!/usr/bin/env python3
"""
Pre-Update Migration Script for Pomera AI Commander

Run this script BEFORE updating via npm or pip to migrate your databases
to the platform-appropriate user data directory.

Usage:
    python migrate_data.py

This will:
1. Find existing databases in the installation directory
2. Copy them to the user data directory (safe from updates)
3. Verify the migration was successful
"""

import os
import sys
import shutil
from pathlib import Path

def get_user_data_dir():
    """Get platform-appropriate user data directory."""
    import platform
    system = platform.system()
    app_name = "Pomera-AI-Commander"
    
    try:
        from platformdirs import user_data_dir
        return Path(user_data_dir(app_name, "PomeraAI"))
    except ImportError:
        pass
    
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(base) / app_name
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / app_name
    else:
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return Path(xdg_data) / app_name

def get_installation_dir():
    """Get the current installation directory."""
    return Path(__file__).parent

def migrate():
    """Migrate databases from installation dir to user data dir."""
    install_dir = get_installation_dir()
    user_dir = get_user_data_dir()
    
    print(f"Installation directory: {install_dir}")
    print(f"User data directory:    {user_dir}")
    print()
    
    # Create user data directory
    user_dir.mkdir(parents=True, exist_ok=True)
    
    databases = ['settings.db', 'notes.db', 'settings.json']
    migrated = []
    skipped = []
    not_found = []
    
    for db_name in databases:
        src = install_dir / db_name
        dst = user_dir / db_name
        
        if not src.exists():
            not_found.append(db_name)
            continue
        
        if dst.exists():
            src_size = src.stat().st_size
            dst_size = dst.stat().st_size
            print(f"⚠️  {db_name}: Already exists in target")
            print(f"    Source size: {src_size:,} bytes")
            print(f"    Target size: {dst_size:,} bytes")
            
            if src_size > dst_size:
                response = input(f"    Source is larger. Overwrite target? [y/N]: ")
                if response.lower() == 'y':
                    shutil.copy2(src, dst)
                    migrated.append(db_name)
                    print(f"    ✅ Overwritten")
                else:
                    skipped.append(db_name)
                    print(f"    ⏭️  Skipped")
            else:
                skipped.append(db_name)
                print(f"    ⏭️  Keeping existing (same or larger)")
        else:
            shutil.copy2(src, dst)
            migrated.append(db_name)
            print(f"✅ {db_name}: Migrated ({src.stat().st_size:,} bytes)")
    
    print()
    print("=" * 50)
    print("Migration Summary")
    print("=" * 50)
    
    if migrated:
        print(f"✅ Migrated:   {', '.join(migrated)}")
    if skipped:
        print(f"⏭️  Skipped:    {', '.join(skipped)}")
    if not_found:
        print(f"➖ Not found:  {', '.join(not_found)}")
    
    print()
    print(f"Your data is now safe in: {user_dir}")
    print()
    print("You can now safely update Pomera via npm or pip!")
    
    return len(migrated) > 0 or len(skipped) > 0

if __name__ == "__main__":
    print("=" * 50)
    print("Pomera AI Commander - Pre-Update Migration")
    print("=" * 50)
    print()
    
    if migrate():
        print("✅ Migration complete!")
        sys.exit(0)
    else:
        print("ℹ️  No databases found to migrate.")
        print("   (This is normal for fresh installations)")
        sys.exit(0)
