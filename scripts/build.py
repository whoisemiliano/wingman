#!/usr/bin/env python3
"""
Build script for Wingman standalone executables.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def install_dependencies():
    """Install build dependencies."""
    print("Installing build dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("✓ Dependencies installed")

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    dirs_to_clean = ["build", "dist", "wingman-dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    print("✓ Build cleaned")

def build_executable():
    """Build the standalone executable."""
    print("Building standalone executable...")
    
    current_platform = platform.system().lower()
    executable_name = "wingman.exe" if current_platform == "windows" else "wingman"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onedir",
        "--name", "wingman",
        "--add-data", "README.md:.",
        "--add-data", "QUICKSTART.md:.",
        "--collect-all", "rich",
        "--hidden-import", "wingman",
        "--hidden-import", "wingman.cli",
        "--hidden-import", "wingman.commands",
        "--hidden-import", "wingman.commands.field_extractor",
        "--hidden-import", "wingman.commands.report_replacer",
        "--hidden-import", "wingman.utils",
        "--hidden-import", "wingman.utils.salesforce_client",
        "--hidden-import", "click",
        "--hidden-import", "rich",
        "--hidden-import", "simple_salesforce",
        "--hidden-import", "pandas",
        "--hidden-import", "yaml",
        "--hidden-import", "requests",
        "wingman/cli.py"
    ]
    
    subprocess.run(cmd, check=True)
    print(f"✓ Executable built: dist/wingman/{executable_name}")

def test_executable():
    """Test the built executable."""
    print("Testing executable...")
    
    current_platform = platform.system().lower()
    executable_name = "wingman.exe" if current_platform == "windows" else "wingman"
    executable_path = f"dist/wingman/{executable_name}"

    if not os.path.exists(executable_path):
        print(f"Error: Executable not found at {executable_path}")
        return False
    
    # Test version command
    try:
        result = subprocess.run([executable_path, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Version test passed: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Version test failed: {e}")
        return False
    
    # Test help command
    try:
        result = subprocess.run([executable_path, "--help"], 
                              capture_output=True, text=True, check=True)
        if "Wingman" in result.stdout:
            print("✓ Help test passed")
        else:
            print("✗ Help test failed: Unexpected output")
            return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Help test failed: {e}")
        return False
    
    return True

def create_distribution_package():
    """Create distribution package."""
    print("Creating distribution package...")
    
    current_platform = platform.system().lower()
    executable_name = "wingman.exe" if current_platform == "windows" else "wingman"
    
    dist_dir = Path("wingman-dist")
    dist_dir.mkdir(exist_ok=True)

    # Copy onedir output (executable + runtime deps)
    for f in Path("dist/wingman").iterdir():
        if f.is_file():
            shutil.copy2(f, dist_dir / f.name)
        else:
            shutil.copytree(f, dist_dir / f.name, dirs_exist_ok=True)

    # Copy documentation
    docs = ["README.md", "QUICKSTART.md"]
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, dist_dir / doc)
    
    # Create installation script
    if current_platform == "windows":
        install_script = dist_dir / "install.bat"
        install_content = '''@echo off
echo Installing Wingman...
echo.
echo Wingman installed! Run: wingman.exe --help
echo.
echo Next steps:
echo 1. Install Salesforce CLI: npm install -g @salesforce/cli
echo 2. Authenticate: sf org login web
echo 3. Test connection: wingman.exe test-connection --org ^<your-org^>
pause
'''
        install_script.write_text(install_content)
    else:
        install_script = dist_dir / "install.sh"
        install_content = '''#!/bin/bash
echo "Installing Wingman..."
chmod +x wingman
echo "Wingman installed! Run: ./wingman --help"
echo ""
echo "Next steps:"
echo "1. Install Salesforce CLI: npm install -g @salesforce/cli"
echo "2. Authenticate: sf org login web"
echo "3. Test connection: ./wingman test-connection --org <your-org>"
'''
        install_script.write_text(install_content)
        os.chmod(install_script, 0o755)
    
    # Calculate package size
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    size_mb = total_size / 1024 / 1024
    
    print(f"✓ Distribution package created in wingman-dist/")
    print(f"✓ Package size: {size_mb:.1f} MB")
    
    return True

def main():
    """Main build process."""
    print("Wingman Build Script")
    print("=" * 30)
    
    try:
        install_dependencies()
        clean_build()
        build_executable()
        
        if test_executable():
            create_distribution_package()
            print("\n" + "=" * 30)
            print("✓ Build completed successfully!")
            print("\nDistribution package created in 'wingman-dist/'")
            print("Users can now run Wingman without Python installed!")
        else:
            print("\n✗ Build failed: Executable tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
