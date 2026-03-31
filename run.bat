@echo off
echo ========================================================
echo   DentNest - Dental Practice Management System
echo ========================================================

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Checking dependencies...
pip install -r requirements.txt

echo Launching DentNest...
python app.py

pause
