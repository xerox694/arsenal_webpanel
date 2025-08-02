# Script PowerShell pour nettoyer les routes dupliquees
$inputFile = "app.py"
$outputFile = "app_clean.py"

# Lire toutes les lignes
$lines = Get-Content $inputFile

$outputLines = @()
$skipLines = $false
$routeCount = 0

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    # Detecter les routes /api/auth/user
    if ($line -match "@app.route\('/api/auth/user'\)") {
        $routeCount++
        
        if ($routeCount -eq 1) {
            Write-Host "Route 1 conservee ligne $($i+1)"
            $outputLines += $line
            $skipLines = $false
        } else {
            Write-Host "Route $routeCount ignoree ligne $($i+1)"
            $skipLines = $true
        }
        continue
    }
    
    # Si on ignore, continuer jusqu'a la prochaine fonction ou route
    if ($skipLines) {
        if ($line -match "^@app.route" -or $line -match "^if __name__" -or $line -match "^# ======") {
            $skipLines = $false
            $outputLines += $line
        }
        continue
    }
    
    # Ajouter la ligne normalement
    $outputLines += $line
}

# Ecrire le fichier nettoye
$outputLines | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "Fichier nettoye cree: $outputFile"
Write-Host "Lignes originales: $($lines.Count)"
Write-Host "Lignes nettoyees: $($outputLines.Count)"
Write-Host "Routes /api/auth/user trouvees: $routeCount"
