@echo off
setlocal

REM Define variables for repository clone and Git user credentials
set REPO_URL=https://github.com/yourusername/yourrepository.git
set GIT_USERNAME="YourUserName"
set GIT_EMAIL="youremail@example.com"
set GIT_TOKEN=your_personal_access_token

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
    set TORTOISEGIT_INSTALLED=true
) else (
    echo TortoiseGit is not installed. Installing the latest version of TortoiseGit...
    powershell -Command "Invoke-WebRequest -Uri 'https://download.tortoisegit.org/tgit/latest64/TortoiseGit-2.14.0.0-64bit.msi' -OutFile '%TORTOISEGIT_INSTALLER%'"
    start /wait msiexec /i %TORTOISEGIT_INSTALLER% /quiet /norestart
    del %TORTOISEGIT_INSTALLER%
)

REM Step 3: Configure TortoiseGit Diff and Merge Tools
REM Replace paths below with paths to your diff and merge tools (e.g., Beyond Compare, WinMerge, KDiff3)

echo Configuring TortoiseGit diff and merge tools...

REM Set up diff tool (e.g., Beyond Compare)
reg add "HKCU\Software\TortoiseGit\DiffTools\BeyondCompare" /v Path /t REG_SZ /d "C:\Program Files\Beyond Compare 4\BCompare.exe" /f
reg add "HKCU\Software\TortoiseGit\DiffTools\BeyondCompare" /v Cmd /t REG_SZ /d "\"C:\Program Files\Beyond Compare 4\BCompare.exe\" \"%base\" \"%mine\"" /f

REM Set up merge tool (e.g., KDiff3)
reg add "HKCU\Software\TortoiseGit\MergeTools\KDiff3" /v Path /t REG_SZ /d "C:\Program Files\KDiff3\kdiff3.exe" /f
reg add "HKCU\Software\TortoiseGit\MergeTools\KDiff3" /v Cmd /t REG_SZ /d "\"C:\Program Files\KDiff3\kdiff3.exe\" \"%theirs\" \"%mine\" \"%base\" -o \"%merged\"" /f
reg add "HKCU\Software\TortoiseGit\MergeTools\KDiff3" /v PreferBinary /t REG_DWORD /d 0 /f
reg add "HKCU\Software\TortoiseGit\MergeTools\KDiff3" /v Extension /t REG_SZ /d "*" /f

REM Step 4: Configure Git credentials
git config --global user.name %GIT_USERNAME%
git config --global user.email %GIT_EMAIL%

REM Step 5: Clone the repository using the token
echo Cloning repository...
git clone https://%GIT_TOKEN%@github.com/yourusername/yourrepository.git

REM Step 6: Clear Git credentials for security
git config --global --unset user.name
git config --global --unset user.email
set GIT_TOKEN=

echo Installation and repository cloning complete.
pause
