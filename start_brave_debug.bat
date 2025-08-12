@echo off
REM Start Brave with remote debugging enabled for Instagram Helper
REM This allows the WSL2 script to connect to your existing Brave instance

echo Stopping any existing Brave processes...
taskkill /f /im brave.exe >nul 2>&1

echo Starting Brave with remote debugging on port 9222...
echo Keep this Brave window open while running the Instagram Helper script.
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

start "" "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222

echo.
echo Brave started with remote debugging enabled.
echo You can now run the Instagram Helper script from WSL2.
echo.
pause
