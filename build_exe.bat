@echo off
REM Build script for DentNest Windows executable

echo ================================================================
echo        Building DentNest Standalone Executable
echo ================================================================
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
pip install -q -r requirements.txt

REM Install PyInstaller
echo Installing PyInstaller...
pip install -q pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM Create data directory
if not exist "data" mkdir data

REM Build the executable
echo.
echo Building standalone executable...
echo This may take 2-5 minutes...
echo.

pyinstaller --clean DentNest.spec

REM Check if build was successful
if exist "dist\DentNest.exe" (
    echo.
    echo ================================================================
    echo                 BUILD SUCCESSFUL!
    echo ================================================================
    echo.
    echo Executable location: dist\DentNest.exe
    echo.
    echo To run the app: cd dist and double-click DentNest.exe
    echo.
    echo To distribute: Copy the dist\DentNest.exe file to any Windows PC
    echo.
) else (
    echo.
    echo BUILD FAILED! Check the output above for errors.
    echo.
    pause
    exit /b 1
)

pause
