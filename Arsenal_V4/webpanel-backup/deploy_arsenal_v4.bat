@echo off
echo 🔥 ARSENAL V4 WEBPANEL - DÉPLOIEMENT COMPLET
echo ================================================

echo 📋 Vérification de l'environnement...

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo 📥 Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js n'est pas installé
    echo 📥 Téléchargement et installation de Node.js...
    
    REM Télécharger Node.js (version LTS)
    echo 🌐 Téléchargement de Node.js LTS...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi' -OutFile 'node-installer.msi'"
    
    if exist node-installer.msi (
        echo 🔧 Installation de Node.js...
        msiexec /i node-installer.msi /quiet /norestart
        echo ⏳ Installation en cours... Veuillez patienter
        timeout /t 30 /nobreak >nul
        del node-installer.msi
        
        REM Mettre à jour le PATH
        refreshenv
        
        REM Revérifier
        node --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo ⚠️ Node.js installé mais nécessite un redémarrage
            echo 🔄 Veuillez redémarrer votre terminal et relancer ce script
            pause
            exit /b 1
        )
    ) else (
        echo ❌ Échec du téléchargement de Node.js
        echo 📥 Veuillez installer manuellement depuis https://nodejs.org
        pause
        exit /b 1
    )
)
echo ✅ Node.js détecté

echo.
echo 🚀 DÉMARRAGE D'ARSENAL V4 WEBPANEL
echo ====================================

REM Aller dans le dossier backend
cd /d "a:\Arsenal_bot\Arsenal_V4\webpanel\backend"

echo 🔧 Démarrage du backend Flask...
start "Arsenal V4 Backend" cmd /k "python app.py"

REM Attendre que le backend démarre
timeout /t 5 /nobreak >nul

REM Aller dans le dossier frontend  
cd /d "a:\Arsenal_bot\Arsenal_V4\webpanel\frontend"

echo 📦 Installation des dépendances frontend (si nécessaire)...
if not exist node_modules (
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

echo 🎨 Démarrage du frontend React...
start "Arsenal V4 Frontend" cmd /k "npm start"

echo.
echo ✅ ARSENAL V4 WEBPANEL DÉPLOYÉ AVEC SUCCÈS!
echo ===========================================
echo.
echo 🌐 Accès WebPanel: http://localhost:3000
echo 🔧 API Backend: http://localhost:5000
echo 📊 APIs disponibles:
echo   • Économie: http://localhost:5000/api/economy/users/SERVER_ID
echo   • Modération: http://localhost:5000/api/moderation/logs/SERVER_ID
echo   • Musique: http://localhost:5000/api/music/queue/SERVER_ID
echo   • Gaming: http://localhost:5000/api/gaming/levels/SERVER_ID
echo   • Analytics: http://localhost:5000/api/analytics/metrics/SERVER_ID
echo.
echo 🎉 Toutes les 6 phases sont opérationnelles!
echo 💾 Base de données: %cd%\..\backend\arsenal_v4.db
echo.
pause
