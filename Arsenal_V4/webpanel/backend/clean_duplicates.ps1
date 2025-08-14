# Script PowerShell pour nettoyer les routes dupliquées
$inputFile = "app.py"
$outputFile = "app_clean.py"

# Lire toutes les lignes
$lines = Get-Content $inputFile

$outputLines = @()
$skipUntilNextRoute = $false
$routesFound = @{}
$insideFunction = $false
$currentRoutePattern = ""

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    # Détecter les routes
    if ($line -match "@app\.route\('/api/auth/user'\)") {
        $routeKey = "/api/auth/user"
        
        if ($routesFound.ContainsKey($routeKey)) {
            Write-Host "🔍 Route dupliquée trouvée ligne $($i+1): $routeKey - IGNORÉE"
            $skipUntilNextRoute = $true
            continue
        } else {
            Write-Host "✅ Route conservée ligne $($i+1): $routeKey"
            $routesFound[$routeKey] = $true
            $skipUntilNextRoute = $false
        }
    }
    
    # Si on ignore une route dupliquée
    if ($skipUntilNextRoute) {
        # Continuer à ignorer jusqu'à la prochaine route ou fonction principale
        if ($line -match "^@app\.route" -or $line -match "^if __name__" -or ($line -match "^def " -and $line -notmatch "def [a-zA-Z_]+\(\):")) {
            # Si c'est une nouvelle route différente, ne plus ignorer
            if ($line -match "^@app\.route" -and -not ($line -match "/api/auth/user")) {
                $skipUntilNextRoute = $false
                $outputLines += $line
            } elseif ($line -match "^if __name__") {
                $skipUntilNextRoute = $false
                $outputLines += $line
            }
            # Sinon continuer à ignorer
        }
        continue
    }
    
    # Ajouter la ligne si on n'ignore pas
    $outputLines += $line
}

# Écrire le fichier nettoyé
$outputLines | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "✅ Fichier nettoyé créé: $outputFile"
Write-Host "📊 Lignes originales: $($lines.Count)"
Write-Host "📊 Lignes nettoyées: $($outputLines.Count)"
