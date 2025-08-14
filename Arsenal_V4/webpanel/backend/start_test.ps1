# Script PowerShell pour démarrer Arsenal V4 WebPanel - Version Propre
Write-Host "🚀 Démarrage d'Arsenal V4 WebPanel - Version Propre" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

# Charger les variables d'environnement depuis .env.test
if (Test-Path ".env.test") {
    Write-Host "📄 Chargement des variables d'environnement depuis .env.test" -ForegroundColor Yellow
    
    Get-Content ".env.test" | ForEach-Object {
        if ($_ -match "^(.+?)=(.+)$") {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "   ✓ $name configuré" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "⚠️ Fichier .env.test non trouvé, utilisation des variables système" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 Configuration:" -ForegroundColor Blue
Write-Host "   - DISCORD_CLIENT_ID: $($env:DISCORD_CLIENT_ID)" -ForegroundColor White
Write-Host "   - DISCORD_REDIRECT_URI: $($env:DISCORD_REDIRECT_URI)" -ForegroundColor White
Write-Host "   - DEBUG: $($env:DEBUG)" -ForegroundColor White

Write-Host ""
Write-Host "🌐 Démarrage du serveur sur http://localhost:5000" -ForegroundColor Green
Write-Host "🔐 Pour tester l'authentification, configurez une vraie app Discord" -ForegroundColor Yellow
Write-Host ""

# Démarrer l'application
python app.py
