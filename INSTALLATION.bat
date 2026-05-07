@echo off
echo [1/2] Creation de l'environnement virtuel...
python -m venv venv
echo [2/2] Installation des bibliotheques...
call venv\Scripts\activate
pip install -r requirements.txt
echo.
echo Installation terminee avec succes !
pause