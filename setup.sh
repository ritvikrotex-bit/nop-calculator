#!/bin/bash

echo "========================================"
echo "Beirman Report Automation App - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH!"
    echo ""
    echo "Please install Python 3.10+ from https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "[OK] Python is installed"
python3 --version
echo ""

# Upgrade pip
echo "[1/4] Upgrading pip..."
python3 -m pip install --upgrade pip
echo ""

# Create virtual environment
echo "[2/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created successfully!"
fi
echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "[4/4] Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo ""

# Verify installation
echo "========================================"
echo "Verifying installation..."
echo "========================================"
python3 -c "import streamlit, pandas, openpyxl, numpy, xlsxwriter, tabulate; print('[OK] All libraries loaded successfully!')"
if [ $? -ne 0 ]; then
    echo "[ERROR] Some libraries failed to import. Please check the error above."
    exit 1
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To run the app:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo ""

