@echo off
echo ========================================
echo Beirman Report Automation App - Setup
echo ========================================
echo.

REM Check if Python is installed (try py launcher first, then python)
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH!
        echo.
        echo Please install Python 3.10+ from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

echo [OK] Python is installed
%PYTHON_CMD% --version
echo.

REM Upgrade pip
echo [1/4] Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    %PYTHON_CMD% -m venv venv
    echo Virtual environment created successfully!
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/4] Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo.

REM Verify installation
echo ========================================
echo Verifying installation...
echo ========================================
python -c "import streamlit, pandas, openpyxl, numpy, xlsxwriter, tabulate; print('[OK] All libraries loaded successfully!')"
if errorlevel 1 (
    echo [ERROR] Some libraries failed to import. Please check the error above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To run the app:
echo   1. Activate the virtual environment: venv\Scripts\activate
echo   2. Run: streamlit run app.py
echo.
pause

