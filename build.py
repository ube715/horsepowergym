"""
Build Script for Horsepower Gym Management System
Creates a standalone Windows executable (.exe)

Usage:
    python build.py

This will create a dist/HorsepowerGym folder containing the executable.
"""

import os
import sys
import subprocess
import shutil


def build_exe():
    """Build the executable using PyInstaller"""
    
    print("=" * 60)
    print("Horsepower Gym - Building Windows Executable")
    print("=" * 60)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    # Check if main.py exists
    if not os.path.exists(main_script):
        print(f"Error: {main_script} not found!")
        return False
    
    # Clean previous builds
    dist_path = os.path.join(script_dir, "dist")
    build_path = os.path.join(script_dir, "build")
    spec_path = os.path.join(script_dir, "HorsepowerGym.spec")
    
    for path in [dist_path, build_path]:
        if os.path.exists(path):
            print(f"Cleaning {path}...")
            shutil.rmtree(path)
    
    if os.path.exists(spec_path):
        os.remove(spec_path)
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=HorsepowerGym",
        "--onedir",  # Create a folder with all files
        "--windowed",  # No console window
        "--noconfirm",  # Replace output directory without asking
        "--clean",  # Clean PyInstaller cache
        # Bundle source modules
        "--add-data", f"{os.path.join(script_dir, 'views')};views",
        "--add-data", f"{os.path.join(script_dir, 'database.py')};.",
        "--add-data", f"{os.path.join(script_dir, 'utils.py')};.",
        # Bundle assets folder for initial structure
        "--add-data", f"{os.path.join(script_dir, 'assets')};assets",
        # Hidden imports for all required libraries
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        "--hidden-import=PIL.ImageFont",
        "--hidden-import=PIL.ImageEnhance",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        # Collect all required packages
        "--collect-all=customtkinter",
        "--collect-all=cv2",
        main_script
    ]
    
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=script_dir, check=True)
        
        if result.returncode == 0:
            exe_path = os.path.join(dist_path, "HorsepowerGym", "HorsepowerGym.exe")
            
            print("\n" + "=" * 60)
            print("BUILD SUCCESSFUL!")
            print("=" * 60)
            print(f"\nExecutable location:")
            print(f"  {exe_path}")
            print(f"\nTo run the application:")
            print(f"  1. Navigate to: {os.path.join(dist_path, 'HorsepowerGym')}")
            print(f"  2. Double-click: HorsepowerGym.exe")
            print("\n" + "=" * 60)
            return True
        else:
            print("\nBuild failed!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return False
    except FileNotFoundError:
        print("\nError: PyInstaller not found!")
        print("Please install it using: pip install pyinstaller")
        return False


def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(script_dir, "requirements.txt")
    
    if os.path.exists(requirements_file):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    else:
        # Install manually if requirements.txt doesn't exist
        packages = ["customtkinter", "pillow", "opencv-python", "numpy", "pyinstaller"]
        for package in packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    print("Requirements installed!")


if __name__ == "__main__":
    print("\nHorsepower Gym - Build Tool")
    print("-" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_requirements()
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        install_requirements()
    
    # Build the executable
    success = build_exe()
    
    if not success:
        print("\nTo install requirements manually, run:")
        print("  pip install -r requirements.txt")
        print("\nThen run this script again:")
        print("  python build.py")
        sys.exit(1)
    
    sys.exit(0)
