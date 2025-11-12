# 🚀 Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Access Streamlit Cloud
Visit: **https://share.streamlit.io**

Sign in with your **GitHub account** (the same one that owns the repository).

---

### 2. Create New App

1. Click **"New app"** button (top right)
2. You'll see a form with these fields:

---

### 3. Configure Your App

Fill in the deployment form:

| Field | Value |
|-------|-------|
| **Repository** | `ritvikrotex-bit/Report-maker-app` |
| **Branch** | `main` (default) |
| **Main file path** | `app.py` |
| **App URL** | (auto-generated) `report-maker-app` |

---

### 4. Advanced Settings (Optional)

Click **"Advanced settings"** to configure:

- **Python version**: `3.10` or `3.11` (recommended)
- **Dependencies**: Streamlit will auto-detect `requirements.txt`
- **Environment variables**: Not needed for this app

---

### 5. Deploy!

Click **"Deploy"** button.

⏳ **Wait 2-5 minutes** while Streamlit Cloud:
- Clones your repository
- Installs dependencies from `requirements.txt`
- Builds and launches your app

---

### 6. Access Your Live App

Once deployment completes, your app will be live at:

**https://report-maker-app.streamlit.app**

(Or the custom URL you chose)

---

## 🔄 Updating Your App

After you push new changes to GitHub:

1. Go to **Streamlit Cloud dashboard**
2. Find your app
3. Click **"⋮" (three dots)** → **"Reboot app"**
4. Or wait ~1 minute for auto-redeploy

---

## 📋 Deployment Checklist

Before deploying, ensure:

- [x] All files are pushed to GitHub
- [x] `requirements.txt` includes all dependencies
- [x] `app.py` is the main entry point
- [x] `.streamlit/config.toml` is committed (if you have custom config)
- [x] No sensitive data in code (use Streamlit secrets if needed)

---

## 🐛 Troubleshooting

### App won't deploy

**Error: "Module not found"**
- Check `requirements.txt` includes all packages
- Verify package names are correct

**Error: "File not found"**
- Ensure `app.py` exists in root directory
- Check file path in deployment settings

**Error: "Port already in use"**
- This is usually a temporary issue
- Wait 1-2 minutes and try again

### App deploys but shows errors

1. Check **Streamlit Cloud logs**:
   - Go to your app dashboard
   - Click **"Manage app"** → **"Logs"**
   - Look for error messages

2. Common issues:
   - Missing dependencies → Add to `requirements.txt`
   - File path issues → Check relative paths in code
   - Environment variables → Configure in Streamlit Cloud settings

---

## 🔐 Security Notes

- **Never commit sensitive data** (API keys, passwords)
- Use **Streamlit Secrets** for sensitive configuration:
  - In Streamlit Cloud: Settings → Secrets
  - Access in code: `st.secrets["my_secret"]`

---

## 📚 Additional Resources

- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Deployment Guide**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Troubleshooting**: https://docs.streamlit.io/streamlit-community-cloud/troubleshooting

---

## ✅ Success!

Once deployed, you can:
- Share your app URL with others
- Embed it in websites
- Use it for monthly report generation
- Access it from any device with internet

---

**Need help?** Check the Streamlit Cloud logs or refer to the troubleshooting section above.

