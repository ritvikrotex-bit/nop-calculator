# Report Maker

A Streamlit-based Python application that processes Excel files and generates financial reports. 
Automates the creation of structured financial reports by comparing multiple Excel sheets (Opening Equity, Closing Equity, and Monthly Summary) and calculating Net Brokerage.

**For detailed system behavior documentation, see:** [`docs/System_Behavior_Guide.md`](docs/System_Behavior_Guide.md)

## 📋 Prerequisites

- **Python 3.10 or higher** (3.10+ recommended)
  - Download from [python.org/downloads](https://www.python.org/downloads/)
  - ⚠️ **Important**: Check "Add Python to PATH" during installation

## 🚀 Quick Setup

### Windows

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH"

2. **Run the setup script**
   ```bash
   setup.bat
   ```

3. **Activate virtual environment and run the app**
   ```bash
   venv\Scripts\activate
   streamlit run app.py
   ```

### Mac / Linux

1. **Install Python 3** (if not already installed)
   ```bash
   # On macOS (using Homebrew)
   brew install python3
   
   # On Ubuntu/Debian
   sudo apt-get install python3 python3-venv python3-pip
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Activate virtual environment and run the app**
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

## 📦 Manual Setup

If you prefer to set up manually:

1. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -c "import streamlit, pandas, openpyxl, numpy, xlsxwriter, tabulate; print('✅ All libraries ready!')"
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
project_root/
│
├── app.py                      # Main Streamlit script
├── requirements.txt            # Python dependencies
├── setup.bat                   # Windows setup script
├── setup.sh                    # Mac/Linux setup script
├── README.md                   # This file
├── data/                       # Folder for sample input Excel files
└── output/                     # Folder to save final report
```

## 📚 Dependencies

- **streamlit** → User interface (file uploads, report preview, download)
- **pandas** → Excel data handling and merging across sheets
- **openpyxl** → Read and write Excel files (.xlsx format)
- **numpy** → Efficient numeric operations
- **xlsxwriter** → Enhanced Excel formatting and styling
- **tabulate** → Formatted table display

## 🎯 Features

- **Smart Header Detection**: Automatically finds header rows in Excel files, even with inconsistent formats
- **Client Filtering**: Filters accounts based on AC Clients List, removing internal/extra accounts
- **Auto Calculations**: 
  - Opening/Closing Equity difference
  - Net Brokerage = Difference - (Deposits - Withdrawals + Credit Out - Credit In + Bonus)
  - Transaction summaries
- **Formatted Output**: Generates Excel reports with styling (bold headers, highlighted Net Brokerage)
- **Account-Level Details**: View individual account calculations alongside summary

## 📋 Required Input Files

1. **AC Clients List** - Excel file containing valid client account numbers
2. **Opening Equity Sheet** - Equity values as of start date
3. **Closing Equity Sheet** - Equity values as of end date
4. **Monthly Summary Sheet** - Transaction data (Deposits, Withdrawals, Credits, Bonus)

## 🔍 Verification

After installation, verify everything works:

```bash
python -m streamlit --version
python -c "import pandas, openpyxl, numpy; print('✅ Libraries Loaded Successfully')"
```

## 🐛 Troubleshooting

### Python not found
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python` on some systems
- Restart your terminal after installing Python

### Virtual environment issues
- Delete the `venv` folder and recreate it
- Make sure you're using the correct Python version

### Import errors
- Activate the virtual environment first
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## 📝 Next Steps

Once setup is complete, the app will be available at:
```
http://localhost:8501
```

## 🚀 Running the App

### Quick Start
```powershell
# Activate virtual environment
venv\Scripts\activate

# Run the app
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`.

### For Deployment
See [`DEPLOYMENT.md`](DEPLOYMENT.md) for local and Streamlit Cloud deployment instructions.

---

**Note**: If you encounter any issues during setup, make sure Python 3.10+ is properly installed and accessible from your command line.
