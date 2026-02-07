@echo off
REM Setup script for MP4 Zoom Viewer (Windows)

echo Setting up MP4 Zoom Viewer development environment...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install package in development mode
echo Installing package in development mode...
pip install -e .

echo.
echo Setup complete!
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To run tests, use:
echo   pytest
