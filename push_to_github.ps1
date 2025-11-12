# Report Maker - Automated GitHub Push Script
# This script automates Git setup, commit, and push to GitHub

param(
    [string]$CommitMessage = "Update: Report Maker - Beirman Formula Edition",
    [string]$GitHubToken = "",
    [string]$RepoName = "Report-maker-app"
)

Write-Host "🚀 Report Maker - GitHub Push Automation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Git is installed
Write-Host "[1/8] Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git for Windows first." -ForegroundColor Red
    exit 1
}

# Step 2: Navigate to project directory
$projectPath = "C:\Users\ritvi\Desktop\Report maker"
Write-Host "[2/8] Navigating to project directory..." -ForegroundColor Yellow
if (Test-Path $projectPath) {
    Set-Location $projectPath
    Write-Host "✅ Project directory: $projectPath" -ForegroundColor Green
} else {
    Write-Host "❌ Project directory not found: $projectPath" -ForegroundColor Red
    exit 1
}

# Step 3: Initialize Git if needed
Write-Host "[3/8] Initializing Git repository..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Step 4: Configure Git identity
Write-Host "[4/8] Configuring Git identity..." -ForegroundColor Yellow
git config --global user.name "ritvikrotex-bit"
git config --global user.email "ritvik.rotex@gmail.com"
Write-Host "✅ Git identity configured" -ForegroundColor Green
Write-Host "   Name: ritvikrotex-bit" -ForegroundColor Gray
Write-Host "   Email: ritvik.rotex@gmail.com" -ForegroundColor Gray

# Step 5: Stage all files
Write-Host "[5/8] Staging all files..." -ForegroundColor Yellow
git add .
$stagedFiles = git status --short | Measure-Object -Line
Write-Host "✅ Staged $($stagedFiles.Lines) files" -ForegroundColor Green

# Step 6: Commit changes
Write-Host "[6/8] Committing changes..." -ForegroundColor Yellow
git commit -m $CommitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changes committed: $CommitMessage" -ForegroundColor Green
} else {
    Write-Host "⚠️  No changes to commit (or commit failed)" -ForegroundColor Yellow
}

# Step 7: Set main branch
Write-Host "[7/8] Setting main branch..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ Branch set to 'main'" -ForegroundColor Green

# Step 8: Configure remote and push
Write-Host "[8/8] Configuring remote and pushing to GitHub..." -ForegroundColor Yellow

# Remove existing remote if it exists
git remote remove origin 2>$null

# Build remote URL
if ($GitHubToken) {
    $remoteUrl = "https://${GitHubToken}@github.com/ritvikrotex-bit/${RepoName}.git"
} else {
    $remoteUrl = "https://github.com/ritvikrotex-bit/${RepoName}.git"
}

# Add remote
git remote add origin $remoteUrl
Write-Host "✅ Remote 'origin' configured: $($remoteUrl -replace $GitHubToken, '***')" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS! Repository uploaded to GitHub" -ForegroundColor Green
    Write-Host "🔗 Repository URL: https://github.com/ritvikrotex-bit/${RepoName}" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Visit: https://github.com/ritvikrotex-bit/${RepoName}" -ForegroundColor White
    Write-Host "   2. Deploy to Streamlit Cloud: https://share.streamlit.io" -ForegroundColor White
    Write-Host "   3. Select repository: ${RepoName}" -ForegroundColor White
    Write-Host "   4. Main file: app.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Push encountered issues:" -ForegroundColor Yellow
    Write-Host $pushResult -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   - If authentication failed, run with token:" -ForegroundColor White
    Write-Host "     .\push_to_github.ps1 -GitHubToken your_token_here" -ForegroundColor Gray
    Write-Host "   - If remote has changes, pull first:" -ForegroundColor White
    Write-Host "     git pull origin main --allow-unrelated-histories" -ForegroundColor Gray
    Write-Host ""
}

