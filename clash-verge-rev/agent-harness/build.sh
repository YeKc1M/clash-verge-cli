#!/bin/bash
# Build script for clash-verge-cli binary

set -e

echo "Building clash-verge-cli binary..."

# Activate virtual environment
source venv/bin/activate

# Run PyInstaller
pyinstaller clash-verge-cli.spec

# Verify binary was created
if [ -f "dist/clash-verge-cli" ]; then
    echo "✓ Binary built successfully: dist/clash-verge-cli"
    echo "Testing binary..."
    ./dist/clash-verge-cli version
else
    echo "✗ Build failed - binary not found"
    exit 1
fi
