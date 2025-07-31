# 📝 Arsenal Changelog System

Ce dossier contient le système de suivi des versions et changelog pour Arsenal V4.

## 📁 Structure

- **`v4.2.6-ULTRA.md`** - Changelog détaillé de la version actuelle
- **`version_info.json`** - Informations de version pour notifications automatiques
- **`update_notifier.py`** - Script Python pour notifier les serveurs des mises à jour
- **`README.md`** - Ce fichier d'aide

## 🚀 Utilisation

### Pour les développeurs
1. **Créer un nouveau changelog** : Copiez `v4.2.6-ULTRA.md` et renommez avec la nouvelle version
2. **Mettre à jour version_info.json** : Changez la version actuelle et les infos d'annonce
3. **Déployer** : Push sur GitHub pour que les notifications soient disponibles

### Pour les administrateurs de serveur
Les notifications peuvent être envoyées automatiquement via le bot Arsenal en utilisant le script `update_notifier.py`.

#### Installation dans le bot :
```python
from changelog.update_notifier import ArsenalUpdateNotifier

# Dans votre bot
update_notifier = ArsenalUpdateNotifier(bot)

# Commande pour annoncer manuellement
@bot.command(name='update_announce')
@commands.has_permissions(administrator=True)
async def announce_update(ctx):
    version_data = await update_notifier.check_for_updates()
    if version_data:
        embed = update_notifier.create_update_embed(version_data)
        await ctx.send(embed=embed)
```

## 🔔 Notifications Automatiques

Le système peut envoyer des notifications Discord avec :
- ✨ Liste des nouvelles fonctionnalités
- 🐛 Corrections de bugs
- 📄 Lien vers le changelog complet
- 🔄 Lien pour redéployer

## 📋 Format Changelog

Utilisez cette structure pour les nouveaux changelogs :

```markdown
# Arsenal VX.X.X - Changelog
**Date de sortie:** DD Mois YYYY
**Développeur:** XeRoX © 2025

## ✨ Nouvelles Fonctionnalités
- Feature 1
- Feature 2

## 🐛 Corrections de Bugs
- Bug fix 1
- Bug fix 2

## 🎯 Améliorations
- Improvement 1
- Improvement 2

**Développé avec ❤️ par XeRoX © 2025**
```

## 🔧 Configuration

Modifiez `version_info.json` pour chaque nouvelle version :

```json
{
    "current_version": "4.X.X",
    "release_date": "YYYY-MM-DD",
    "announcement": {
        "title": "🚀 Arsenal VX.X.X est disponible !",
        "description": "Description des changements",
        "features": [
            "🎨 Nouvelle fonctionnalité 1",
            "🐛 Correction bug important"
        ]
    }
}
```

---

**Développé par XeRoX © 2025**
