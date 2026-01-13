@echo off
echo Resetting database and starting servers...
echo.

echo Deleting old database...
if exist backend\classroom.db del backend\classroom.db

echo Starting Backend (will create new database)...
start "Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Servers are starting with fresh database...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo You can now register new accounts!
echo Press any key to exit this window...
pause >nul