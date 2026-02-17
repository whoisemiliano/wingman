#!/usr/bin/env python3
"""
Verify Wingman is installed correctly by importing the package and checking the CLI.
"""
import subprocess
import sys


def main():
    # Check package import
    try:
        import wingman
        print(f"✓ Wingman package imported (version {wingman.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import wingman: {e}")
        sys.exit(1)

    # Check CLI is on PATH and runs
    try:
        result = subprocess.run(
            [sys.executable, "-m", "wingman.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            print(f"✓ CLI runs: {result.stdout.strip()}")
        else:
            print(f"✗ CLI failed: {result.stderr or result.stdout}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ CLI check failed: {e}")
        sys.exit(1)

    print("✓ Installation check passed.")


if __name__ == "__main__":
    main()
