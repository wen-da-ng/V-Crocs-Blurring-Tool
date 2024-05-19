@echo off
REM Change directory to the script's location
cd %~dp0

REM Optionally activate a virtual environment (if you're using one)
call .venv\Scripts\activate

REM Run the application
streamlit run app.py

REM Pause the command line to view any output or errors
pause
