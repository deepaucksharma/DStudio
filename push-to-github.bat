@echo off
REM Git Push Script for DStudio Repository (Windows)

echo Setting up Git repository for DStudio...

REM Initialize git if not already initialized
if not exist ".git" (
    git init
    echo Git repository initialized.
)

REM Add remote if not already added
git remote | findstr /C:"origin" >nul
if errorlevel 1 (
    git remote add origin https://github.com/deepaucksharma/DStudio.git
    echo Remote origin added.
)

REM Add all files
git add .
echo All files added to staging.

REM Commit with a message
set /p commit_message="Enter commit message (or press Enter for default): "

if "%commit_message%"=="" (
    set commit_message=System Design Implementation Guide - Complete architecture with code examples
)

git commit -m "%commit_message%"

REM Force push to overwrite existing content
echo Warning: This will overwrite all existing content in the repository!
set /p confirmation="Are you sure you want to continue? (yes/no): "

if /i "%confirmation%"=="yes" (
    git push -f origin main
    echo Code pushed successfully!
) else (
    echo Push cancelled.
)

pause
