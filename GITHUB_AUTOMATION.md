# 🚀 GitHub Automation Guide

## Quick Push to GitHub

This project includes an automated script that handles all Git operations in one command.

---

## 📋 Prerequisites

- ✅ Git installed and accessible (`git --version` works)
- ✅ GitHub repository exists: `ritvikrotex-bit/Report-maker-app`
- ✅ You're in the project directory: `C:\Users\ritvi\Desktop\Report maker`

---

## 🎯 Method 1: Automated Script (Recommended)

### Basic Usage

```powershell
.\push_to_github.ps1
```

This will:
1. ✅ Check Git installation
2. ✅ Initialize repository (if needed)
3. ✅ Configure Git identity
4. ✅ Stage all files
5. ✅ Commit with default message
6. ✅ Push to GitHub

### Custom Commit Message

```powershell
.\push_to_github.ps1 -CommitMessage "Your custom commit message here"
```

### With GitHub Token (for authentication)

```powershell
.\push_to_github.ps1 -GitHubToken "ghp_your_token_here"
```

### All Options

```powershell
.\push_to_github.ps1 `
    -CommitMessage "Update: Added new feature" `
    -GitHubToken "ghp_your_token_here" `
    -RepoName "Report-maker-app"
```

---

## 🎯 Method 2: Manual Git Commands

If you prefer manual control:

### 1. Stage All Files
```powershell
git add .
```

### 2. Commit Changes
```powershell
git commit -m "Your commit message"
```

### 3. Push to GitHub
```powershell
git push origin main
```

---

## 🔐 Authentication

### Option A: Personal Access Token (PAT)

1. **Create a token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control)
   - Copy the token

2. **Use in script:**
   ```powershell
   .\push_to_github.ps1 -GitHubToken "ghp_your_token_here"
   ```

### Option B: Git Credential Manager

Git will prompt for credentials automatically. Use your GitHub username and PAT as password.

---

## 📝 What Gets Pushed

The script automatically:
- ✅ Stages all project files
- ✅ Respects `.gitignore` (excludes `venv/`, sample Excel files, etc.)
- ✅ Commits changes
- ✅ Pushes to `main` branch

### Files Included:
- `app.py`
- `data_processor.py`
- `requirements.txt`
- `README.md`
- `DEPLOYMENT.md`
- `docs/`
- `.streamlit/config.toml`
- Setup scripts

### Files Excluded (via `.gitignore`):
- `venv/` (virtual environment)
- Sample Excel files (`*.xlsx` in root)
- `__pycache__/`
- IDE folders (`.cursor/`, `.vscode/`, etc.)

---

## 🐛 Troubleshooting

### Error: "Git is not installed"
**Solution:** Install Git for Windows from https://git-scm.com/download/win

### Error: "Authentication failed"
**Solution:** 
- Use PAT: `.\push_to_github.ps1 -GitHubToken "your_token"`
- Or configure Git Credential Manager

### Error: "Remote contains work that you don't have locally"
**Solution:**
```powershell
git pull origin main --allow-unrelated-histories
git push origin main
```

### Error: "Repository not found"
**Solution:**
- Verify repository name: `Report-maker-app` (capital R)
- Check you have push access
- Verify remote URL: `git remote -v`

---

## ✅ Success Indicators

After running the script, you should see:

```
✅ SUCCESS! Repository uploaded to GitHub
🔗 Repository URL: https://github.com/ritvikrotex-bit/Report-maker-app
```

---

## 🔄 Workflow Example

### Daily Development Workflow

1. **Make changes** to your code
2. **Test locally** (`streamlit run app.py`)
3. **Push to GitHub:**
   ```powershell
   .\push_to_github.ps1 -CommitMessage "Fixed login normalization bug"
   ```
4. **Deploy** (if using Streamlit Cloud, it auto-deploys)

---

## 📚 Related Documentation

- **Deployment Guide:** [`deploy_to_streamlit.md`](deploy_to_streamlit.md)
- **Full Deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)
- **System Behavior:** [`docs/System_Behavior_Guide.md`](docs/System_Behavior_Guide.md)

---

## 🎉 Next Steps

After pushing to GitHub:

1. ✅ **Verify on GitHub:** https://github.com/ritvikrotex-bit/Report-maker-app
2. 🚀 **Deploy to Streamlit Cloud:** See [`deploy_to_streamlit.md`](deploy_to_streamlit.md)
3. 📊 **Share your app** with others!

---

**Need help?** Check the troubleshooting section or refer to the main [`README.md`](README.md).

