# Report Maker - Deployment Guide

## 🚀 Local Deployment (Current Setup)

### Running Locally

1. **Activate virtual environment:**
   ```powershell
   venv\Scripts\activate
   ```

2. **Run Streamlit app:**
   ```powershell
   streamlit run app.py
   ```

3. **Access the app:**
   - The app will automatically open in your default browser
   - Or manually navigate to: `http://localhost:8501`

### Stopping the App

- Press `Ctrl+C` in the terminal where Streamlit is running
- Or close the terminal window

---

## ☁️ Streamlit Cloud Deployment

### Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

### Deployment Steps

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Report Maker"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Environment:**
   - Streamlit Cloud will automatically detect `requirements.txt`
   - No additional configuration needed for basic deployment

### Streamlit Cloud Configuration

Create `.streamlit/config.toml` (already created):
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### File Upload Limits

- **Streamlit Cloud**: 200MB per file upload limit
- For larger files, consider using cloud storage (S3, Google Drive) integration

---

## 🔒 Security Considerations

### For Production Deployment

1. **Environment Variables:**
   - Store sensitive data in Streamlit Cloud secrets
   - Access via `st.secrets["key"]`

2. **File Access:**
   - Uploaded files are stored in memory (temporary)
   - Consider persistent storage for production

3. **Authentication:**
   - Streamlit Cloud provides basic authentication
   - For advanced security, use Streamlit's authentication features

---

## 📝 Deployment Checklist

- [x] Code is in GitHub repository
- [x] `requirements.txt` is up to date
- [x] `.streamlit/config.toml` is configured
- [x] All dependencies are listed
- [x] App runs successfully locally
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud app created
- [ ] App deployed and tested

---

## 🐛 Troubleshooting

### Local Issues

**Port already in use:**
```powershell
# Kill existing Streamlit process
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"} | Stop-Process
```

**Import errors:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Streamlit Cloud Issues

**Build fails:**
- Check `requirements.txt` for all dependencies
- Verify Python version compatibility (3.10+)

**App crashes:**
- Check Streamlit Cloud logs
- Verify file paths are relative (not absolute)
- Ensure all imports are available

---

## 📊 Current Status

✅ **Local deployment ready**
- App runs on `http://localhost:8501`
- All dependencies installed
- Configuration files in place

⏳ **Streamlit Cloud deployment:**
- Ready for deployment once code is on GitHub
- No additional configuration needed

---

© TDFX Capital — Automated Report Maker | Beirman Formula Edition

