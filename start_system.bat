@echo off
:: This script now only starts the Python applications.
:: ngrok is started manually via a button in the cashier app.

:: Set the current directory to this file's location
cd /d "%~dp0"

:: Define the Python executable from our bundled venv
SET PYTHON_EXE=.\venv\Scripts\python.exe

:: Start the three apps invisibly in the background
START "WebApp" /B %PYTHON_EXE% web_app/app.py
START "PCApp" /B %PYTHON_EXE% pc_app/cashier_app.py
START "ReportGen" /B %PYTHON_EXE% report_generator/attractive_image_generator.py