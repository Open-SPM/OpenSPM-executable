@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo Creating Optimized Portable Python for LabVIEW
echo ==============================================

:: Create directory structure
set PROJECT_DIR=%~dp0
set PYTHON_DIR=%PROJECT_DIR%python
set SCRIPTS_DIR=%PROJECT_DIR%scripts
set TEMP_DIR=%PROJECT_DIR%temp

echo Creating directories...
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
if not exist "%SCRIPTS_DIR%" mkdir "%SCRIPTS_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Set Python version and URL
set PYTHON_VERSION=3.9.13
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_ZIP=%TEMP_DIR%\python-%PYTHON_VERSION%-embed-amd64.zip

:: Download Python embedded package
echo Downloading embedded Python %PYTHON_VERSION%...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'"
if %errorlevel% neq 0 (
    echo Failed to download Python.
    goto :error
)

:: Extract Python
echo Extracting Python...
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
if %errorlevel% neq 0 (
    echo Failed to extract Python.
    goto :error
)

:: Enable site-packages in embedded Python
echo Configuring Python for pip...
set PTHFILE=%PYTHON_DIR%\python%PYTHON_VERSION:~0,1%%PYTHON_VERSION:~2,1%._pth
if exist "%PTHFILE%" (
    powershell -Command "(Get-Content '%PTHFILE%') -replace '#import site', 'import site' | Set-Content '%PTHFILE%'"
)

:: Download and install pip
echo Installing pip...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP_DIR%\get-pip.py'"
"%PYTHON_DIR%\python.exe" "%TEMP_DIR%\get-pip.py" --no-warn-script-location
if %errorlevel% neq 0 (
    echo Failed to install pip.
    goto :error
)

:: Initial optimization - remove unnecessary pip files
echo Initial optimization - removing unnecessary pip files...
if exist "%PYTHON_DIR%\Lib\site-packages\pip\_vendor\distlib\t32" rd /s /q "%PYTHON_DIR%\Lib\site-packages\pip\_vendor\distlib\t32"
if exist "%PYTHON_DIR%\Lib\site-packages\pip\_vendor\distlib\t64" rd /s /q "%PYTHON_DIR%\Lib\site-packages\pip\_vendor\distlib\t64"

:: Install required packages based on the imports
echo Installing required packages...

echo Installing lxml for XML processing...
"%PYTHON_DIR%\python.exe" -m pip install lxml --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install lxml, continuing...

echo Installing matplotlib==3.0.1...
"%PYTHON_DIR%\python.exe" -m pip install matplotlib==3.0.1 --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install matplotlib, continuing...

echo Installing pyparsing==2.4.7...
"%PYTHON_DIR%\python.exe" -m pip install pyparsing==2.4.7 --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install pyparsing, continuing...

echo Installing pywin32 for Windows COM interface...
"%PYTHON_DIR%\python.exe" -m pip install pywin32 --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install pywin32, continuing...

echo Installing opencv-python...
"%PYTHON_DIR%\python.exe" -m pip install opencv-python --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install opencv-python, continuing...

echo Installing numpy for numerical operations...
"%PYTHON_DIR%\python.exe" -m pip install numpy --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install numpy, continuing...

echo Installing imageio for image reading (primary choice)...
"%PYTHON_DIR%\python.exe" -m pip install imageio --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install imageio, continuing...

echo Installing scikit-image as fallback for image reading...
"%PYTHON_DIR%\python.exe" -m pip install scikit-image --no-warn-script-location
if %errorlevel% neq 0 echo Warning: Failed to install scikit-image, continuing...

:: Optimization steps after installation
echo Running optimization to reduce size...

:: 1. Clean pip cache
echo Cleaning pip cache...
"%PYTHON_DIR%\python.exe" -m pip cache purge

:: 2. Remove test directories
echo Removing test directories...
if exist "%PYTHON_DIR%\Lib\test" rd /s /q "%PYTHON_DIR%\Lib\test"
if exist "%PYTHON_DIR%\Lib\unittest\test" rd /s /q "%PYTHON_DIR%\Lib\unittest\test"

:: 3. Remove __pycache__ directories
echo Removing __pycache__ directories...
for /d /r "%PYTHON_DIR%" %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d"
)

:: 4. Remove .pyc files
echo Removing .pyc files...
for /r "%PYTHON_DIR%" %%f in (*.pyc) do (
    del "%%f"
)

:: 5. Remove documentation files
echo Removing documentation files...
for /r "%PYTHON_DIR%" %%f in (*.html *.txt *.rst *.md) do (
    del "%%f"
)

:: 6. Remove tests from installed packages
echo Removing tests from installed packages...
for /d /r "%PYTHON_DIR%\Lib\site-packages" %%d in (tests test) do (
    if exist "%%d" rd /s /q "%%d"
)

:: 7. Remove example data and documentation
for /d /r "%PYTHON_DIR%\Lib\site-packages" %%d in (examples docs) do (
    if exist "%%d" rd /s /q "%%d"
)

:: Clean up temporary files
echo Cleaning up...
del "%PYTHON_ZIP%"
del "%TEMP_DIR%\get-pip.py"
rmdir "%TEMP_DIR%"

:: Get the size of the Python installation
for /f "usebackq tokens=3" %%s in (`dir /s /-c "%PYTHON_DIR%" ^| findstr "bytes$"`) do set TOTAL_SIZE=%%s
set /a SIZE_MB=%TOTAL_SIZE:~0,-3%/1024

echo ==============================================
echo Optimized Portable Python setup completed!
echo.
echo Total size: Approximately %SIZE_MB% MB
echo.
echo Python location: %PYTHON_DIR%\python.exe
echo Test your setup by running: test_python.bat
echo Configure LabVIEW using: labview_config.bat
echo ==============================================

goto :end

:error
echo ==============================================
echo Error occurred during setup.
echo Please check the error messages above.
echo ==============================================
exit /b 1

:end
endlocal