#!/bin/bash
# Build script for clash-verge-cli binary

set -e

echo "Building clash-verge-cli binary..."

# Activate virtual environment
source venv/bin/activate

# Run PyInstaller with output to project root (two levels up from agent-harness)
pyinstaller --distpath=../.. clash-verge-cli.spec

# Verify binary was created
if [ -f "../../clash-verge-cli" ]; then
    echo "✓ Binary built successfully: ../../clash-verge-cli"
    echo "Testing binary..."
    ../../clash-verge-cli version
else
    echo "✗ Build failed - binary not found"
    exit 1
fi
