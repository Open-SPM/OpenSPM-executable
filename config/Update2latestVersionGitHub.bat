@echo off
REM Navigate to the parent directory
cd ..

REM Create the tempconfig folder if it doesn't exist
set TEMP_DIR=..\tempconfig
if not exist "%TEMP_DIR\NUL%" (
    mkdir "%TEMP_DIR%"
)

REM Copy the config and UserConfig folders to tempconfig
xcopy "config" "%TEMP_DIR%\config" /s /y /i
xcopy "UserConfig" "%TEMP_DIR%\UserConfig" /s /y /i

REM Set up Git user credentials
git config user.name "YourUserName"
git config user.email "youremail@example.com"

REM Set your Git token in the remote URL for authentication
set GIT_TOKEN=your_personal_access_token
set REPO_URL=https://%GIT_TOKEN%@github.com/marcospenedo/OpenSPM-source.git

REM Pull changes from the remote main branch
git stash
git pull origin main

REM Clear the token for security
set GIT_TOKEN=

REM Copy back the config and UserConfig folders from tempconfig to the repository root
robocopy "%TEMP_DIR%\config" "config" /s /xf "Menu.rtm" "InstallOpenSPM.bat" "Update2latestVersionGitHub.bat"
xcopy "%TEMP_DIR%\UserConfig" "UserConfig" /s /y /i

REM Remove the tempconfig directory
rmdir /s /q "%TEMP_DIR%"

REM Optional: Remove Git user configuration if necessary
git config --unset user.name
git config --unset user.email

REM Display a success message
echo Script completed successfully. All operations finished without errors.

pause
