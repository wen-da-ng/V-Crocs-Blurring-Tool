@echo off
setlocal

REM Define the full path to Python 3.9 explicitly
set PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe

REM Check if the specified Python exists
if not exist "%PYTHON_EXE%" (
    echo Python 3.9 executable not found at "%PYTHON_EXE%".
    echo Please ensure Python 3.9 is installed correctly.
    pause
    exit /b
)

REM Create and activate virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating a virtual environment...
    "%PYTHON_EXE%" -m venv .venv
    echo Virtual environment created.
)

REM Activate the virtual environment
call .venv\Scripts\activate

REM Define the path to the installation flag file
set FLAG_FILE=.venv\install_complete.flag

REM Check if the flag file exists to determine if dependencies need to be installed
if exist "%FLAG_FILE%" (
    echo Dependencies already installed, skipping installation.
) else (
    REM Install PyTorch with CUDA 11.8 support
    echo Installing PyTorch with CUDA 11.8 support...
    %PYTHON_EXE% -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

    REM Install other requirements
    echo Installing required packages from requirements.txt...
    pip install --upgrade -r requirements.txt

    REM Create a flag file to indicate successful installation
    echo > "%FLAG_FILE%"
    echo Installation complete.
)

REM Run the application
echo Running the application...
streamlit run app.py

REM Pause the command line to view any output or errors
pause
