@echo off
echo Lancement du serveur Backend...
call venv\Scripts\activate
start "" "frontend/index.html"
python backend/app.py
pause