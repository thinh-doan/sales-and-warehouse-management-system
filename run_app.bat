@echo off
REM Run the application from project root
cd /d "%~dp0"
python main.py %*
