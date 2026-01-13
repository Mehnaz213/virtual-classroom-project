@echo off
echo Quick Test - Live Alerts System
echo ================================
echo.

echo 1. Starting fresh servers...
if exist backend\classroom.db del backend\classroom.db
start "Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo 2. Servers starting...
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:5173
echo.

echo 3. Test Instructions:
echo    a) Go to http://localhost:5173
echo    b) Register as Teacher (choose TEACHER role)
echo    c) Create session with code "TEST01"
echo    d) Open incognito window
echo    e) Register as Student (choose STUDENT role)  
echo    f) Join session with code "TEST01"
echo    g) In teacher window, click on the session
echo    h) In student window, switch tabs (Ctrl+T)
echo    i) Check teacher dashboard for alerts!
echo.

echo 4. Debugging:
echo    - Press F12 in student window to see console logs
echo    - Look for "[Tab Switch] Event sent" messages
echo    - Teacher dashboard updates every 5 seconds
echo.

echo Press any key when done testing...
pause >nul