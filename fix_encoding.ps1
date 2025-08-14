# Script pour corriger l'encodage des caractères
$content = Get-Content "demo_gems_modal.html" -Raw -Encoding UTF8

# Corriger les caractères accentués
$content = $content -replace "Ã©", "é"
$content = $content -replace "Ã¨", "è"
$content = $content -replace "Ã ", "à"
$content = $content -replace "Ã¢", "â"
$content = $content -replace "Ã´", "ô"
$content = $content -replace "Ã¹", "ù"
$content = $content -replace "Ã»", "û"
$content = $content -replace "Ã®", "î"
$content = $content -replace "Ã§", "ç"
$content = $content -replace "Ã‰", "É"
$content = $content -replace "Ã€", "À"

# Corriger les emojis corrompus
$content = $content -replace "ðŸ"Š", "📊"
$content = $content -replace "ðŸ†", "🏆"
$content = $content -replace "âš¡", "⚡"
$content = $content -replace "ðŸ'¥", "💥"
$content = $content -replace "â¤ï¸", "❤️"
$content = $content -replace "ðŸƒ", "🏃"
$content = $content -replace "â­", "⭐"
$content = $content -replace "ðŸª™", "🪙"
$content = $content -replace "âš"ï¸", "⚔️"
$content = $content -replace "ðŸ§Ÿ", "🧟"
$content = $content -replace "ðŸ''", "👑"
$content = $content -replace "ðŸ"¥", "🔥"
$content = $content -replace "ðŸ"ˆ", "📈"
$content = $content -replace "ðŸ"", "📊"
$content = $content -replace "ðŸ'Ž", "💎"
$content = $content -replace "ï¿½ï¸", "🛡️"

# Sauvegarder le fichier corrigé
$content | Out-File "demo_gems_modal.html" -Encoding UTF8NoBOM
Write-Host "Encodage corrigé!"
