@echo off
echo ========================================
echo LinkedIn Automation Setup
echo ========================================
echo.

echo Installing dependencies...
uv sync

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Add your credentials to .env
echo 3. Run: get_token.bat
echo 4. Run: test.bat
echo 5. Run: run.bat
echo.
pause
