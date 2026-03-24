@echo off
echo Starting VitalSync Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Resolve Firebase credentials path from .env (fallback to serviceAccountKey.json)
set "FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json"
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if /I "%%A"=="FIREBASE_CREDENTIALS_PATH" set "FIREBASE_CREDENTIALS_PATH=%%B"
    )
)
set "FIREBASE_CREDENTIALS_PATH=%FIREBASE_CREDENTIALS_PATH:"=%"
if "%FIREBASE_CREDENTIALS_PATH:~0,2%"=="./" set "FIREBASE_CREDENTIALS_PATH=%FIREBASE_CREDENTIALS_PATH:~2%"

REM Check for Firebase credentials
if not exist "%FIREBASE_CREDENTIALS_PATH%" (
    echo Warning: %FIREBASE_CREDENTIALS_PATH% not found!
    echo Please add your Firebase service account key before running.
    pause
    exit /b 1
)

REM Start server
echo.
echo Starting server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
