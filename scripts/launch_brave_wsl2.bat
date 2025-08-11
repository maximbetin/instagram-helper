@echo off
REM Launch Windows Brave with remote debugging enabled for WSL2 access
REM This script helps launch Brave from Windows with the correct flags

setlocal enabledelayedexpansion

REM Default values
set DEBUG_PORT=9222
set INSTAGRAM_URL=https://www.instagram.com/

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="-p" (
    set DEBUG_PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-u" (
    set INSTAGRAM_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    goto :show_help
)
if "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args
:end_parse

echo Launching Windows Brave with remote debugging...
echo Debug port: %DEBUG_PORT%
echo URL: %INSTAGRAM_URL%
echo.

REM Try different Brave paths
set BRAVE_PATH=
for %%p in (
    "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    "C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
) do (
    if exist %%p (
        set BRAVE_PATH=%%p
        goto :found_brave
    )
)

echo Error: Brave browser not found in common locations.
echo Please install Brave or set BROWSER_PATH environment variable.
exit /b 1

:found_brave
echo Found Brave at: %BRAVE_PATH%

REM Launch Brave with remote debugging
echo Starting Brave with remote debugging enabled...
start "" "%BRAVE_PATH%" --remote-debugging-port=%DEBUG_PORT% --remote-debugging-address=0.0.0.0 "%INSTAGRAM_URL%"

echo.
echo Brave launched successfully!
echo Remote debugging available at: http://localhost:%DEBUG_PORT%
echo.
echo Security note: This exposes the debugging port on your Windows host network.
echo Consider using Windows Firewall to restrict access if needed.
echo.
echo You can now run your Python script from WSL2.
goto :end

:show_help
echo Usage: %~nx0 [OPTIONS]
echo Launch Windows Brave with remote debugging for WSL2 access
echo.
echo Options:
echo   -p PORT    Debug port (default: 9222)
echo   -u URL     URL to open (default: https://www.instagram.com/)
echo   -h         Show this help message
echo.
echo Example:
echo   %~nx0 -p 9223 -u https://example.com

:end
