@echo off
title Employee Management SaaS - CBSE Class 12 Project
echo Launching Employee Management SaaS System...
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error. Press any key to exit.
    pause > nul
)
