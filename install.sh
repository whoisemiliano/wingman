#!/bin/bash
# Wingman Universal Installer
# One-line install: curl -sSL https://raw.githubusercontent.com/whoisemiliano/wingman/master/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

REPO="whoisemiliano/wingman"

print_status "Wingman Universal Installer"
print_status "================================="

# Optional: install specific version (e.g. v0.1.0). Default: latest release.
VERSION="${WINGMAN_VERSION:-}"
if [ -z "$VERSION" ]; then
    print_status "Fetching latest release version..."
    VERSION=$(curl -sSL "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    if [ -z "$VERSION" ]; then
        print_error "Could not determine latest version. Set WINGMAN_VERSION or check https://github.com/$REPO/releases"
        exit 1
    fi
fi
print_status "Version: $VERSION"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_status "Detected platform: $PLATFORM"

if [ "$PLATFORM" = "windows" ]; then
    PACKAGE="wingman-windows.zip"
    EXECUTABLE="wingman.exe"
else
    PACKAGE="wingman-$PLATFORM.tar.gz"
    EXECUTABLE="wingman"
fi

print_status "Downloading Wingman $VERSION for $PLATFORM..."

# Install into a dedicated dir (not ~/.local/bin/wingman) so the symlink can live at ~/.local/bin/wingman
INSTALL_DIR="${WINGMAN_INSTALL_DIR:-$HOME/.local/share/wingman}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION/$PACKAGE"
if ! curl -fSL --progress-bar --connect-timeout 30 --max-time 300 -o "$PACKAGE" "$DOWNLOAD_URL"; then
    print_error "Download failed. Check that $VERSION exists at https://github.com/$REPO/releases"
    exit 1
fi

if [ "$PLATFORM" = "windows" ]; then
    unzip -o "$PACKAGE" || true
else
    tar -xzf "$PACKAGE"
fi

if [ "$PLATFORM" != "windows" ]; then
    # We are in INSTALL_DIR (we did cd earlier); make binary executable
    chmod +x "$EXECUTABLE"
    # macOS: remove quarantine so Gatekeeper doesn't block the downloaded binary
    if [[ "$OSTYPE" == "darwin"* ]]; then
        xattr -d com.apple.quarantine "$EXECUTABLE" 2>/dev/null || true
    fi
    # Symlink: use absolute path so it works from any cwd
    INSTALL_DIR_ABS="$(pwd)"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$INSTALL_DIR_ABS/$EXECUTABLE" "$HOME/.local/bin/wingman"
fi
rm -f "$PACKAGE"

print_success "Wingman installed successfully!"
print_status "Location: $INSTALL_DIR"

if [ "$PLATFORM" != "windows" ]; then
    print_status "Added to PATH: ~/.local/bin/wingman"
fi

print_status ""
print_status "Next steps:"
print_status "1. Install Salesforce CLI: npm install -g @salesforce/cli"
print_status "2. Authenticate: sf org login web"
print_status "3. Test connection: wingman test-connection --org <your-org>"
print_status "4. Get help: wingman --help"
