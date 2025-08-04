# ================================================================
# 🧹 ARSENAL CLEANUP SCRIPT - NETTOYAGE COMPLET
# ================================================================
# Supprime tous les fichiers test*, start*, et autres brouillons
# Garde seulement les ORIGINAUX identifiés
# ================================================================

Write-Host "🧹 ARSENAL CLEANUP - Debut du nettoyage..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Yellow

# Compteur pour les statistiques
$FilesDeleted = 0
$TotalSize = 0

# ================================================================
# FONCTION DE SUPPRESSION SÉCURISÉE
# ================================================================
function Remove-SafeFile {
    param($FilePath, $Description)
    
    if (Test-Path $FilePath) {
        $size = (Get-Item $FilePath).Length
        $global:TotalSize += $size
        $global:FilesDeleted++
        
        Write-Host "❌ Suppression: $Description" -ForegroundColor Red
        Write-Host "   └── $FilePath" -ForegroundColor Gray
        Remove-Item $FilePath -Force
    }
}

# ================================================================
# SUPPRESSION FICHIERS TEST*
# ================================================================
Write-Host "`n🎯 Suppression des fichiers TEST*..." -ForegroundColor Yellow

Get-ChildItem -Path "a:\Arsenal_bot" -Recurse -File | Where-Object { 
    $_.Name -match "^test" 
} | ForEach-Object {
    Remove-SafeFile $_.FullName "Test file: $($_.Name)"
}

# ================================================================
# SUPPRESSION FICHIERS START*
# ================================================================
Write-Host "`n🎯 Suppression des fichiers START*..." -ForegroundColor Yellow

Get-ChildItem -Path "a:\Arsenal_bot" -Recurse -File | Where-Object { 
    $_.Name -match "^start" 
} | ForEach-Object {
    Remove-SafeFile $_.FullName "Start script: $($_.Name)"
}

# ================================================================
# CRÉATION DOSSIER BACKUP
# ================================================================
Write-Host "`n📦 Création du dossier BACKUP..." -ForegroundColor Green

$BackupDir = "a:\Arsenal_bot\BACKUP_FILES"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
    Write-Host "✅ Dossier BACKUP_FILES créé" -ForegroundColor Green
}

# ================================================================
# DÉPLACEMENT FICHIERS APP* NON ORIGINAUX VERS BACKUP
# ================================================================
Write-Host "`n🎯 Déplacement des fichiers APP* créés après le 27/07/2025 vers BACKUP..." -ForegroundColor Yellow

$KeepApps = @("advanced_server.py", "app_corrupted.py") # Les 2 originaux identifiés

Get-ChildItem -Path "a:\Arsenal_bot\Arsenal_V4\webpanel\backend" -File | Where-Object { 
    $_.Name -match "^app" -and 
    $_.Name -notin $KeepApps -and
    $_.CreationTime -gt (Get-Date "27/07/2025 23:59:59")
} | ForEach-Object {
    $dest = Join-Path $BackupDir $_.Name
    Move-Item $_.FullName $dest -Force
    Write-Host "📦 Déplacé vers BACKUP: $($_.Name)" -ForegroundColor Blue
}

# ================================================================
# DÉPLACEMENT BROUILLONS VERS BACKUP
# ================================================================
Write-Host "`n🎯 Déplacement des brouillons vers BACKUP..." -ForegroundColor Yellow

$BrouillonPatterns = @(
    "*revolutionary*",
    "*backup*", 
    "*_old*",
    "*_new*",
    "*_clean*",
    "*_fixed*",
    "*temp*",
    "*tmp*"
)

foreach ($pattern in $BrouillonPatterns) {
    Get-ChildItem -Path "a:\Arsenal_bot" -Recurse -File | Where-Object { 
        $_.Name -like $pattern -and $_.FullName -notlike "*BACKUP_FILES*"
    } | ForEach-Object {
        $dest = Join-Path $BackupDir $_.Name
        # Si le fichier existe déjà, ajouter un timestamp
        if (Test-Path $dest) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $name = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
            $ext = [System.IO.Path]::GetExtension($_.Name)
            $dest = Join-Path $BackupDir "$name`_$timestamp$ext"
        }
        Move-Item $_.FullName $dest -Force
        Write-Host "📦 Brouillon vers BACKUP: $($_.Name)" -ForegroundColor Blue
    }
}

# ================================================================
# SUPPRESSION DOSSIERS VIDES
# ================================================================
Write-Host "`n🎯 Suppression des dossiers vides..." -ForegroundColor Yellow

Get-ChildItem -Path "a:\Arsenal_bot" -Recurse -Directory | Where-Object {
    (Get-ChildItem $_.FullName -Recurse -File).Count -eq 0
} | ForEach-Object {
    Write-Host "📁 Dossier vide supprimé: $($_.Name)" -ForegroundColor Gray
    Remove-Item $_.FullName -Force -Recurse
}

# ================================================================
# CRÉATION DOSSIER README
# ================================================================
Write-Host "`n📚 Création du dossier README..." -ForegroundColor Green

$ReadmeDir = "a:\Arsenal_bot\README_DOCS"
if (-not (Test-Path $ReadmeDir)) {
    New-Item -ItemType Directory -Path $ReadmeDir -Force
    Write-Host "✅ Dossier README_DOCS créé" -ForegroundColor Green
}

# Déplacer tous les README* vers le dossier
Get-ChildItem -Path "a:\Arsenal_bot" -Recurse -File | Where-Object { 
    $_.Name -match "^README" -or $_.Name -match "\.md$"
} | ForEach-Object {
    $dest = Join-Path $ReadmeDir $_.Name
    if ($_.FullName -ne $dest) {
        Move-Item $_.FullName $dest -Force
        Write-Host "📝 README déplacé: $($_.Name)" -ForegroundColor Green
    }
}

# ================================================================
# RAPPORT FINAL
# ================================================================
Write-Host "`n================================================================" -ForegroundColor Yellow
Write-Host "🎉 NETTOYAGE TERMINÉ!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "📊 Statistiques:" -ForegroundColor Cyan
Write-Host "   └── Fichiers supprimés: $FilesDeleted" -ForegroundColor White
Write-Host "   └── Espace libéré: $([math]::Round($TotalSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host "`n✅ FICHIERS CONSERVÉS (ORIGINAUX):" -ForegroundColor Green
Write-Host "   └── advanced_server.py (PRINCIPAL)" -ForegroundColor White
Write-Host "   └── app_corrupted.py (RÉFÉRENCE)" -ForegroundColor White
Write-Host "`n📦 FICHIERS SAUVEGARDÉS:" -ForegroundColor Blue
Write-Host "   └── Tous les backups dans BACKUP_FILES/" -ForegroundColor White
Write-Host "   └── Tous les README dans README_DOCS/" -ForegroundColor White

Write-Host "`n🚀 Arsenal est maintenant PROPRE et prêt!" -ForegroundColor Cyan

# Pause pour voir le résultat
Read-Host "`nAppuyez sur Entrée pour continuer..."
