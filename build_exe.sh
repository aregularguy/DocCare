#!/bin/bash
# Build script for DentNest Windows executable

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🦷 Building DentNest Standalone Executable             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt

# Install PyInstaller if not already installed
echo "✓ Installing PyInstaller..."
pip install -q pyinstaller

# Clean previous builds
echo "✓ Cleaning previous builds..."
rm -rf build dist __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Create data directory if it doesn't exist
mkdir -p data

# Build the executable
echo ""
echo "🔨 Building standalone executable..."
echo "   This may take 2-5 minutes..."
echo ""

pyinstaller --clean DentNest.spec

# Check if build was successful
if [ -f "dist/DentNest" ] || [ -f "dist/DentNest.exe" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  ✅ BUILD SUCCESSFUL!                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📦 Executable location:"
    echo "   $(pwd)/dist/DentNest"
    echo ""
    echo "📏 File size:"
    du -h dist/DentNest* | awk '{print "   " $1}'
    echo ""
    echo "🚀 To run the app:"
    echo "   cd dist"
    echo "   ./DentNest"
    echo ""
    echo "📤 To distribute:"
    echo "   1. Copy the 'dist/DentNest' file to any Windows machine"
    echo "   2. Double-click to run (no installation needed!)"
    echo ""
else
    echo ""
    echo "❌ Build failed! Check the output above for errors."
    echo ""
    exit 1
fi
