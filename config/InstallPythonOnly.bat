REM Step 7: Install Python 3.9 (64-bit) and Required Packages

REM Define Python installer URL and paths
set PYTHON_INSTALLER=%TEMP%\PythonInstaller.exe
set PYTHON_URL=https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe

REM Check if Python 3.9 is already installed
python --version 2>nul | findstr "3.9" >nul
if %errorlevel% equ 0 (
    echo Python 3.9 is already installed.
) else (
    echo Downloading and installing Python 3.9...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    del %PYTHON_INSTALLER%
)

REM Verify Python installation
python --version
if %errorlevel% neq 0 (
    echo Python installation failed. Exiting.
    exit /b 1
)

REM Upgrade pip to the latest version
python -m pip install --upgrade pip --user

REM Install required Python packages
echo Installing required Python packages...
python -m pip install click --user
python -m pip install matplotlib==3.0.1 --user
python -m pip install numpy --user
python -m pip install Pillow --user
python -m pip install pyqt5 --user
python -m pip install scikit-image --user
python -m pip install scipy --user
python -m pip install pywin32 --user
python -m pip install pyparsing==2.4.7 --user
python -m pip install lxml --user

REM Verify installed packages
python -m pip show matplotlib pyparsing numpy Pillow pyqt5 scikit-image scipy pywin32 click lxml

echo Python installation and package setup complete.

echo Installation and repository cloning complete.

pause