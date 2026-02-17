#!/usr/bin/env python3
"""
Version management script for Wingman.
"""

import re
import sys
import subprocess
from pathlib import Path

def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return None
    
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    return match.group(1) if match else None

def update_version(new_version):
    """Update version in all relevant files."""
    files_to_update = [
        "pyproject.toml",
        "setup.py",
        "wingman/__init__.py"
    ]
    
    for file_path in files_to_update:
        path = Path(file_path)
        if not path.exists():
            continue
            
        content = path.read_text()
        
        if file_path == "pyproject.toml":
            content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
        elif file_path == "setup.py":
            content = re.sub(r'version="[^"]+"', f'version="{new_version}"', content)
        elif file_path == "wingman/__init__.py":
            content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
        
        path.write_text(content)
        print(f"✓ Updated {file_path}")

def create_git_tag(version):
    """Create and push git tag."""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    try:
        subprocess.run(["git", "tag", "-l", tag_name], check=True, capture_output=True)
        if tag_name in subprocess.run(["git", "tag", "-l"], capture_output=True, text=True).stdout:
            print(f"Tag {tag_name} already exists")
            return False
    except subprocess.CalledProcessError:
        pass
    
    # Create and push tag (use current branch, not hardcoded main)
    current_branch = (
        subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        .stdout.strip()
    )
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], check=True)
    subprocess.run(["git", "push", "origin", current_branch], check=True)
    subprocess.run(["git", "push", "origin", tag_name], check=True)
    
    print(f"✓ Created and pushed tag {tag_name}")
    return True

def main():
    """Main version management function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/version.py <new_version>")
        print("Example: python scripts/version.py 1.0.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("Error: Version must be in format X.Y.Z (e.g., 1.0.0)")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    if current_version == new_version:
        print("Version is already set to this value")
        sys.exit(0)
    
    # Update version in files
    print("Updating version in files...")
    update_version(new_version)
    
    # Create git tag
    print("Creating git tag...")
    if create_git_tag(new_version):
        print(f"\n✓ Version updated to {new_version}")
        print("GitHub Actions will automatically build and create a release!")
    else:
        print(f"\n✓ Version updated to {new_version}")
        print("Note: Git tag already exists, no release will be triggered")

if __name__ == '__main__':
    main()
