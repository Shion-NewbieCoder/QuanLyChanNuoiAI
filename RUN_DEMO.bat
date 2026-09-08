@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "BOOTSTRAP=%PROJECT_ROOT%tools\run_demo.py"

if not exist "%BOOTSTRAP%" (
    echo [BOOTSTRAP_MISSING] tools\run_demo.py was not found.
    echo Next action: Extract or clone the complete project, then run this file again.
    goto :fatal
)

rem Detect a Python 3 launcher first; tools\run_demo.py performs the exact
rem supported-version check so unsupported Python reports PYTHON_UNSUPPORTED.
py -3 -c "import sys; raise SystemExit(0 if sys.version_info.major == 3 else 1)" >nul 2>&1
if not errorlevel 1 goto :run_with_py

python -c "import sys; raise SystemExit(0 if sys.version_info.major == 3 else 1)" >nul 2>&1
if not errorlevel 1 goto :run_with_python

echo [PYTHON_MISSING] Python 3 was not found.
echo Install Python 3.12 or newer and make it available through the Windows Python launcher
echo or PATH, then run the project again.
goto :fatal

:run_with_py
pushd "%PROJECT_ROOT%"
py -3 "%BOOTSTRAP%" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
goto :finish

:run_with_python
pushd "%PROJECT_ROOT%"
python "%BOOTSTRAP%" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
goto :finish

:fatal
set "EXIT_CODE=1"

:finish
if not "%EXIT_CODE%"=="0" (
    echo.
    echo Demo startup failed with exit code %EXIT_CODE%.
    if /I not "%TERM_PROGRAM%"=="vscode" pause
)
exit /b %EXIT_CODE%
