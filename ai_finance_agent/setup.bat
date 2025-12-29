@echo off
echo Setting up AI Finance Agent...

echo.
echo 1. Installing frontend dependencies...
call npm install

echo.
echo 2. Installing backend dependencies...
cd backend
call pip install -r requirements.txt
cd ..

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Get your FREE GROQ API key from: https://console.groq.com/
echo 2. Set your GROQ API key: set GROQ_API_KEY=your-key-here
echo 3. Run start-backend.bat in one terminal
echo 4. Run start-frontend.bat in another terminal
echo 5. Open http://localhost:3000 in your browser
echo.
pause