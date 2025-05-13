#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil

def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("Building standalone executable...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # Change to the script directory
    
    # Install required packages
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    
    # Build the executable
    print("Building executable...")
    subprocess.check_call([
        "pyinstaller",
        "--clean",
        "dropbox_renamer.spec"
    ])
    
    # Create dist directory if it doesn't exist
    dist_dir = os.path.join(script_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    
    # The executable is now in dist/dropbox-renamer/dropbox-renamer
    if sys.platform == "win32":
        source_dir = os.path.join(dist_dir, "dropbox-renamer")
        dest_dir = os.path.join(dist_dir, "dropbox-renamer-windows")
    else:
        source_dir = os.path.join(dist_dir, "dropbox-renamer")
        dest_dir = os.path.join(dist_dir, "dropbox-renamer-macos")
    
    # Create a zip file of the distribution
    print("Creating distribution package...")
    shutil.make_archive(dest_dir, 'zip', source_dir)
    
    print(f"\nBuild complete! The distribution package is in: {dest_dir}.zip")
    print("You can distribute this zip file along with the .env file.")
    print("Users should extract the zip file and run the executable inside.")

if __name__ == "__main__":
    build_executable() 