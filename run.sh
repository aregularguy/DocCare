#!/bin/bash
# Quick start script for DentNest

echo "🦷 Starting DentNest - Dental Practice Management System"
echo "========================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.dependencies_installed
fi

# Run the application
echo "Launching DentNest..."
python -m src.main
