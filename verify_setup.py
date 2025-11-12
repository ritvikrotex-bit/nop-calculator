"""
Enhanced Status Check for Beirman Report Automation
Run this to get a complete environment status report.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True, f"{version.major}.{version.minor}.{version.micro}"
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.10+")
        return False, f"{version.major}.{version.minor}.{version.micro}"

def check_venv():
    """Check if virtual environment exists and is active"""
    venv_exists = os.path.exists('venv')
    is_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if venv_exists:
        print(f"✅ Virtual environment 'venv/' - EXISTS")
    else:
        print(f"⚠️  Virtual environment 'venv/' - NOT FOUND (run setup.bat to create)")
    
    if is_active:
        print(f"✅ Virtual environment - ACTIVE")
    else:
        print(f"⚠️  Virtual environment - NOT ACTIVE")
        print(f"   Activate with: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")
    
    return venv_exists, is_active

def check_imports():
    """Check if all required libraries can be imported"""
    libraries = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'openpyxl': 'OpenPyXL',
        'numpy': 'NumPy',
        'xlsxwriter': 'XlsxWriter',
        'tabulate': 'Tabulate'
    }
    
    results = {}
    all_ok = True
    for lib, name in libraries.items():
        try:
            module = __import__(lib)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {name} - OK (v{version})")
            results[name] = {'status': 'OK', 'version': version}
        except ImportError as e:
            print(f"❌ {name} - NOT FOUND")
            print(f"   Error: {str(e)}")
            results[name] = {'status': 'NOT FOUND', 'error': str(e)}
            all_ok = False
    
    return all_ok, results

def check_directories():
    """Check if required directories exist"""
    dirs = ['data', 'output']
    all_ok = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}/' - OK")
        else:
            print(f"❌ Directory '{dir_name}/' - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_files():
    """Check if required files exist"""
    files = ['app.py', 'requirements.txt']
    all_ok = True
    
    for file_name in files:
        if os.path.exists(file_name):
            print(f"✅ File '{file_name}' - OK")
        else:
            print(f"❌ File '{file_name}' - NOT FOUND")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("Beirman Report Automation - Environment Status Check")
    print("=" * 60)
    print()
    
    print("1. Checking Python version...")
    python_ok, python_version = check_python_version()
    print()
    
    print("2. Checking virtual environment...")
    venv_exists, venv_active = check_venv()
    print()
    
    print("3. Checking required libraries...")
    imports_ok, import_results = check_imports()
    print()
    
    print("4. Checking project directories...")
    dirs_ok = check_directories()
    print()
    
    print("5. Checking project files...")
    files_ok = check_files()
    print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_checks = python_ok and imports_ok and dirs_ok and files_ok
    
    if all_checks and venv_active:
        print("✅ All checks passed! Environment is ready.")
        print()
        print("You can now run:")
        print("  streamlit run app.py")
    elif all_checks and not venv_active:
        print("⚠️  Dependencies installed, but virtual environment not active.")
        print()
        print("Activate it with:")
        print("  Windows: venv\\Scripts\\activate")
        print("  Mac/Linux: source venv/bin/activate")
    else:
        print("❌ Some checks failed. Action required:")
        print()
        if not python_ok:
            print("  • Install Python 3.10+ from https://www.python.org/downloads/")
        if not venv_exists:
            print("  • Create virtual environment: python -m venv venv")
        if not imports_ok:
            print("  • Install dependencies: pip install -r requirements.txt")
            if not venv_active:
                print("    (Make sure venv is activated first!)")
        if not dirs_ok:
            print("  • Create missing directories")
        if not files_ok:
            print("  • Verify project files are present")
    
    print()
    print("=" * 60)
    
    return 0 if all_checks else 1

if __name__ == "__main__":
    sys.exit(main())
