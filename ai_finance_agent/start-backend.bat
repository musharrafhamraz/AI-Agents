@echo off
echo Starting AI Finance Agent Backend...
echo.
echo Testing GROQ integration first...
python test_groq.py
echo.
if %ERRORLEVEL% EQU 0 (
    echo Starting main backend...
    python simple_main.py
) else (
    echo Please fix the issues above before starting the backend.
    pause
)