@echo off
setlocal
cd /d "%~dp0"
py -3 -c "import sys; assert sys.version_info >= (3,12)" >nul 2>&1
if not errorlevel 1 (
    py -3 tools\build_demo.py
    goto :finish
)
python -c "import sys; assert sys.version_info >= (3,12)" >nul 2>&1
if not errorlevel 1 (
    python tools\build_demo.py
    goto :finish
)
echo BUILD_PYTHON_MISSING: Developer build requires Python 3.12 or newer.
exit /b 1
:finish
if errorlevel 1 (
    echo BUILD_FAILED: Review the output above. Close a running DEMO.exe before rebuilding.
    exit /b 1
)
echo Portable demo is ready in DEMO_PORTABLE\DEMO.exe
exit /b 0
