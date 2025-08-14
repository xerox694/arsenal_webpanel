@echo off
REM 🚀 Script de déploiement Arsenal V4 sur Render (Windows)

echo 🚀 Arsenal V4 - Déploiement Render
echo ==================================

REM Vérification Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git n'est pas installé
    pause
    exit /b 1
)

REM Initialisation Git si nécessaire
if not exist ".git" (
    echo 📦 Initialisation du repository Git...
    git init
    git branch -M main
)

REM Ajouter tous les fichiers
echo 📁 Ajout des fichiers...
git add .

REM Commit
echo 💾 Commit des changements...
git commit -m "🚀 Arsenal V4 - Configuration complète pour Render"

REM Configuration remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 🔗 Configuration remote GitHub...
    echo ⚠️  Configurez votre remote GitHub:
    echo    git remote add origin https://github.com/xerox694/arsenal_webpanel.git
    echo    git push -u origin main
) else (
    echo 📤 Push vers GitHub...
    git push origin main
)

echo.
echo ✅ Préparation terminée !
echo.
echo 🌐 Étapes suivantes:
echo 1. Aller sur render.com
echo 2. Connecter votre repository GitHub
echo 3. Configurer les variables d'environnement
echo 4. Déployer !
echo.
echo 📖 Documentation complète: DEPLOY_RENDER_GUIDE.md
pause
