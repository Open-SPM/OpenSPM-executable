@echo off
setlocal

REM Define variables for repository clone and Git user credentials
set REPO_URL=https://github.com/marcospenedo/OpenSPM-source.git
set GIT_USERNAME="username"
set GIT_EMAIL="email"
set GIT_TOKEN=token

REM Paths for temporary installers
set TEMP_DIR=%TEMP%
set GIT_INSTALLER=%TEMP_DIR%\GitInstaller.exe
set TORTOISEGIT_INSTALLER=%TEMP_DIR%\TortoiseGitInstaller.msi

REM Step 1: Check if Git is installed
where git.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo Git is already installed.
    set GIT_INSTALLED=true
) else (
    echo Git is not installed. Installing the latest version of Git...
    powershell -Command "(Invoke-RestMethod -Uri 'https://api.github.com/repos/git-for-windows/git/releases/latest').assets | Where-Object { $_.name -match '64-bit.exe' } | ForEach-Object { Invoke-WebRequest -Uri $_.browser_download_url -OutFile '%GIT_INSTALLER%' }"
    start /wait %GIT_INSTALLER% /VERYSILENT /NORESTART
    del %GIT_INSTALLER%
)

REM Step 2: Check if TortoiseGit is installed
where TortoiseGitProc.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo TortoiseGit is already installed.
) else (
    echo TortoiseGit is not installed. Installing the latest version of TortoiseGit...

    REM Download TortoiseGit installer
    powershell -Command "Invoke-WebRequest -Uri 'https://download.tortoisegit.org/tgit/2.17.0.0/TortoiseGit-2.17.0.0-64bit.msi' -OutFile '%TEMP%\TortoiseGitInstaller.msi'"
    
    REM Verify download
    if not exist "%TEMP%\TortoiseGitInstaller.msi" (
        echo Failed to download TortoiseGit installer. Please check the URL or network connectivity.
        exit /b 1
    )

    REM Install TortoiseGit with logging
    echo Installing TortoiseGit...
    start /wait msiexec /i "%TEMP%\TortoiseGitInstaller.msi" /norestart /log "%TEMP%\TortoiseGitInstall.log"
    
    REM Check installation result
    if %errorlevel% neq 0 (
        echo Failed to install TortoiseGit. Check the log file at %TEMP%\TortoiseGitInstall.log.
        del "%TEMP%\TortoiseGitInstaller.msi"
        pause
        exit /b 1
    )

    REM Cleanup
    del "%TEMP%\TortoiseGitInstaller.msi"
    echo TortoiseGit installation completed successfully.
)

REM Step 3: Configure TortoiseGit Diff and Merge Tools
REM Replace paths below with paths to your diff and merge tools (e.g., Beyond Compare, WinMerge, KDiff3)

echo Configuring TortoiseGit diff and merge tools...

REM Configure TortoiseGit Diff and Merge Tools for LabVIEW files

REM Set up diff tool (LabVIEW Compare)
reg add "HKCU\Software\TortoiseGit\DiffTools\LVCompare" /v Path /t REG_SZ /d "C:\Program Files\National Instruments\Shared\LabVIEW Compare\LVCompare.exe" /f
reg add "HKCU\Software\TortoiseGit\DiffTools\LVCompare" /v Cmd /t REG_SZ /d "\"C:\Program Files\National Instruments\Shared\LabVIEW Compare\LVCompare.exe\" \"%base\" \"%mine\"" /f
reg add "HKCU\Software\TortoiseGit\DiffTools\LVCompare" /v Extension /t REG_SZ /d ".vi;.vit;.lvproj;.lvlps;.aliases;.lvlib;.vim;.lvbitx;.rtm;.ctl" /f

REM Set up merge tool (LabVIEW Merge)
reg add "HKCU\Software\TortoiseGit\MergeTools\LVMerge" /v Path /t REG_SZ /d "C:\Program Files\National Instruments\Shared\LabVIEW Merge\LVMerge.exe" /f
reg add "HKCU\Software\TortoiseGit\MergeTools\LVMerge" /v Cmd /t REG_SZ /d "\"C:\Program Files\National Instruments\Shared\LabVIEW Merge\LVMerge.exe\" \"%theirs\" \"%mine\" \"%base\" -o \"%merged\"" /f
reg add "HKCU\Software\TortoiseGit\MergeTools\LVMerge" /v PreferBinary /t REG_DWORD /d 0 /f
reg add "HKCU\Software\TortoiseGit\MergeTools\LVMerge" /v Extension /t REG_SZ /d ".vi;.vit;.lvproj;.lvlps;.aliases;.lvlib;.vim;.lvbitx;.rtm;.ctl" /f

REM Step 4: Configure Git credentials
git config --global user.name %GIT_USERNAME%
git config --global user.email %GIT_EMAIL%

REM Step 5: Clone the repository using the token
echo Cloning repository...
git clone https://%GIT_TOKEN%@github.com/marcospenedo/OpenSPM-source.git

REM Step 6: Clear Git credentials for security
git config --global --unset user.name
git config --global --unset user.email
set GIT_TOKEN=

REM Step 7: Install Python 3.6 (64-bit) and Required Packages

REM Define Python installer URL and paths
set PYTHON_INSTALLER=%TEMP%\PythonInstaller.exe
set PYTHON_URL=https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe

REM Check if Python 3.6 is already installed
python --version 2>nul | findstr "3.6" >nul
if %errorlevel% equ 0 (
    echo Python 3.6 is already installed.
) else (
    echo Downloading and installing Python 3.6...
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

REM Verify installed packages
python -m pip show matplotlib pyparsing numpy Pillow pyqt5 scikit-image scipy pywin32 click

echo Python installation and package setup complete.

echo Installation and repository cloning complete.

pause
