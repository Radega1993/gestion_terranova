@echo off
echo Building GestionTerranova for Windows...

REM Create and activate virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Ensure Babel is installed correctly
echo Reinstalling Babel...
pip uninstall -y babel
pip install babel==2.14.0

REM Build the executable
echo Building executable...
pyinstaller GestionTerranova.spec

echo Build complete! The executable is in the dist folder.
echo.
pause 