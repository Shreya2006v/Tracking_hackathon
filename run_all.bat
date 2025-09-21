@echo off
title Bus Tracking Prototype

REM Start backend
start cmd /k "cd backend && python app.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start GPS simulator
start cmd /k "cd simulator && python gps_sim.py"

REM Open frontend in default browser
start "" "frontend\index.html"

echo All processes started. Backend and simulator running.
pause
