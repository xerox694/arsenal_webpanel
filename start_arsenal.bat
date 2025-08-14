@echo off
title Arsenal V4 - Launcher Ultra
color 0A

echo.
echo  ========================================
echo   🚀 ARSENAL V4 - LAUNCHER AUTOMATIQUE
echo  ========================================
echo.
echo  🌐 WebPanel: http://localhost:5000
echo  🤖 Bot Discord: Démarrage automatique
echo  📊 Logs temps réel disponibles
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou non trouvé dans PATH
    echo    Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)

:: Installer les dépendances si nécessaire
echo 📦 Vérification des dépendances...
pip install flask flask-socketio requests >nul 2>&1

:: Créer les répertoires nécessaires
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo ✅ Dépendances vérifiées
echo.

:: Démarrer le système avec bot automatique
echo 🚀 Démarrage du système complet...
echo    - WebPanel sur http://localhost:5000
echo    - Bot Discord en arrière-plan
echo    - Logs en temps réel
echo.

:: Lancer le webpanel avec auto-start du bot
python webpanel_advanced.py --start-bot

echo.
echo ⚠️ Arrêt du système détecté
pause
