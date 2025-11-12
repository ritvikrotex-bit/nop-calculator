@echo off
REM Quick GitHub Push Script for Report Maker
REM Usage: push.bat [commit_message]

setlocal

if "%1"=="" (
    set COMMIT_MSG=Update: Report Maker - Beirman Formula Edition
) else (
    set COMMIT_MSG=%*
)

echo.
echo ========================================
echo   Report Maker - GitHub Push
echo ========================================
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1" -CommitMessage "%COMMIT_MSG%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Push completed successfully!
) else (
    echo.
    echo ❌ Push failed. Check errors above.
    exit /b 1
)

endlocal

