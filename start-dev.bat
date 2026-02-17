@echo off
echo Starting LLM Council in Development Mode...
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create a .env file with your OpenRouter API key.
    pause
    exit /b 1
)

echo Starting Backend on port 8001...
start "LLM Council Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --reload --port 8001"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend on port 5173...
start "LLM Council Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ============================================
echo   LLM Council is starting!
echo ============================================
echo.
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5173
echo.
echo   Opening browser in 5 seconds...
echo ============================================

timeout /t 5 /nobreak >nul
start http://localhost:5173
