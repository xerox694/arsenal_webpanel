@echo off
echo 🚀 Démarrage d'Arsenal V4 WebPanel - Version Propre
echo =====================================================

REM Charger les variables d'environnement de test
for /f "delims=" %%x in (.env.test) do (set "%%x")

echo ✅ Variables d'environnement chargées
echo 🔧 Configuration:
echo    - DISCORD_CLIENT_ID: %DISCORD_CLIENT_ID%
echo    - DISCORD_REDIRECT_URI: %DISCORD_REDIRECT_URI%
echo    - DEBUG: %DEBUG%

echo.
echo 🌐 Démarrage du serveur sur http://localhost:5000
echo 🔐 Pour tester l'authentification, configurez une vraie app Discord
echo.

python app.py

pause
