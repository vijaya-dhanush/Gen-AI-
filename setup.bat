@echo off
echo ============================================
echo   LLM Council - Production Ready Setup
echo ============================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your OpenRouter API key:
    echo   1. Copy .env.example to .env
    echo   2. Add your API key from https://openrouter.ai/keys
    echo.
    pause
    exit /b 1
)

echo [1/4] Installing backend dependencies...
cd /d "%~dp0"
pip install -e . >nul 2>&1
if errorlevel 1 (
    echo Installing with uv...
    uv pip install -e .
)

echo [2/4] Installing frontend dependencies...
cd frontend
call npm install

echo [3/4] Building frontend for production...
call npm run build

echo [4/4] Setup complete!
echo.
echo ============================================
echo   To run the application:
echo ============================================
echo.
echo   Option 1 - Development mode:
echo     Terminal 1: cd backend ^&^& uvicorn main:app --reload --port 8001
echo     Terminal 2: cd frontend ^&^& npm run dev
echo.
echo   Option 2 - Use start-dev.bat
echo.
echo   Then open: http://localhost:5173
echo ============================================
pause
