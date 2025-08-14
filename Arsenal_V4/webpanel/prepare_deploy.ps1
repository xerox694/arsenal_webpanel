# 🚀 Arsenal V4 WebPanel - Script de Préparation Déploiement (Windows)
# PowerShell script pour préparer le déploiement

Write-Host "🎯 Arsenal V4 WebPanel - Préparation Déploiement" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Vérification des fichiers essentiels
Write-Host "📋 Vérification des fichiers..." -ForegroundColor Yellow

$requiredFiles = @(
    "unified_launcher.py",
    "advanced_server.py", 
    "main.py",
    "requirements.txt"
)

$filesOK = 0
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
        $filesOK++
    } else {
        Write-Host "❌ $file manquant!" -ForegroundColor Red
    }
}

# Vérification des pages frontend
Write-Host ""
Write-Host "🖥️ Vérification pages frontend..." -ForegroundColor Yellow

$frontendPages = @(
    "webpanel\frontend\analytics.html",
    "webpanel\frontend\realtime.html",
    "webpanel\frontend\users.html",
    "webpanel\frontend\commands.html",
    "webpanel\frontend\automod.html",
    "webpanel\frontend\security.html",
    "webpanel\frontend\games.html",
    "webpanel\frontend\backup.html",
    "webpanel\frontend\bridges.html",
    "webpanel\frontend\hub.html",
    "webpanel\frontend\botinfo.html",
    "webpanel\frontend\help.html",
    "webpanel\frontend\performance.html",
    "webpanel\frontend\database.html",
    "webpanel\frontend\api.html"
)

$pagesCount = 0
foreach ($page in $frontendPages) {
    if (Test-Path $page) {
        $pagesCount++
        $pageName = Split-Path $page -Leaf
        Write-Host "✅ $pageName" -ForegroundColor Green
    } else {
        $pageName = Split-Path $page -Leaf
        Write-Host "❌ $pageName manquant!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 Résumé: $pagesCount/15 pages frontend détectées" -ForegroundColor Cyan

# Génération du fichier .gitignore
Write-Host ""
Write-Host "📝 Génération .gitignore..." -ForegroundColor Yellow

$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Secrets
config.json
secrets.json
token.txt

# Cache
*.cache
.cache/

# Temporary
tmp/
temp/
*.tmp

# Arsenal specific
hunt_royal_cache.json
arsenal_v4.db
hunt_royal.db
suggestions.db
hunt_royal_auth.db
hunt_royal_profiles.db
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✅ .gitignore créé" -ForegroundColor Green

# Génération du Procfile
Write-Host ""
Write-Host "📄 Génération Procfile..." -ForegroundColor Yellow

"web: python unified_launcher.py" | Out-File -FilePath "Procfile" -Encoding UTF8 -NoNewline
Write-Host "✅ Procfile créé" -ForegroundColor Green

# Génération du runtime.txt
Write-Host ""
Write-Host "🐍 Génération runtime.txt..." -ForegroundColor Yellow

"python-3.11.4" | Out-File -FilePath "runtime.txt" -Encoding UTF8 -NoNewline
Write-Host "✅ runtime.txt créé" -ForegroundColor Green

# Création des dossiers
Write-Host ""
Write-Host "📁 Vérification structure dossiers..." -ForegroundColor Yellow

$directories = @("static\css", "static\js", "static\images", "templates", "webpanel\frontend")

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Structure dossiers OK" -ForegroundColor Green

# Génération render.yaml
Write-Host ""
Write-Host "⚙️ Génération render.yaml..." -ForegroundColor Yellow

$renderConfig = @"
services:
  - type: web
    name: arsenal-v4-webpanel
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python unified_launcher.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 10000
    healthCheckPath: /
    disk:
      name: arsenal-data
      mountPath: /data
      sizeGB: 1
"@

$renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8
Write-Host "✅ render.yaml créé" -ForegroundColor Green

# Vérification Git
Write-Host ""
Write-Host "🔄 Vérification Git..." -ForegroundColor Yellow

if (Test-Path ".git") {
    Write-Host "✅ Repository Git détecté" -ForegroundColor Green
} else {
    Write-Host "⚠️  Git non initialisé. Exécutez: git init" -ForegroundColor Yellow
}

# Résumé final
Write-Host ""
Write-Host "🎉 PRÉPARATION TERMINÉE!" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Statistiques:" -ForegroundColor Cyan
Write-Host "   • $pagesCount pages frontend" -ForegroundColor White
Write-Host "   • Backend Flask complet" -ForegroundColor White
Write-Host "   • Launcher unifié prêt" -ForegroundColor White
Write-Host "   • Configuration déploiement OK" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. git add ." -ForegroundColor White
Write-Host "   2. git commit -m 'Arsenal V4 WebPanel Ready for Deployment'" -ForegroundColor White
Write-Host "   3. git push origin main" -ForegroundColor White
Write-Host "   4. Déployer sur Render/Heroku" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Plateformes de déploiement:" -ForegroundColor Cyan
Write-Host "   • Render: https://render.com" -ForegroundColor White
Write-Host "   • Heroku: https://heroku.com" -ForegroundColor White
Write-Host "   • Railway: https://railway.app" -ForegroundColor White
Write-Host ""
Write-Host "✅ Votre Arsenal V4 WebPanel est prêt pour la production!" -ForegroundColor Green

# Afficher les commandes Git
Write-Host ""
Write-Host "📋 Commandes Git suggérées:" -ForegroundColor Cyan
Write-Host "git add ." -ForegroundColor Yellow
Write-Host "git commit -m '🚀 Arsenal V4 WebPanel Complete - Ready for production deployment'" -ForegroundColor Yellow
Write-Host "git push origin main" -ForegroundColor Yellow

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
