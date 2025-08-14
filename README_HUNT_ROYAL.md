# 🏹 HUNT ROYAL & SYSTÈME DE MODULES - Arsenal Bot V4

## 📋 Vue d'ensemble

Ce système fournit un module Hunt Royal complet avec système de suggestions avancé et rechargement à chaud (hot-reload) pour Arsenal Bot V4.

### 🎯 Fonctionnalités Principales

- **Module Hunt Royal** : Base de données complète avec chasseurs, donjons, équipements, gemmes
- **Système de Suggestions** : Suggestions avancées avec votes et modération
- **Hot-Reload** : Rechargement des modules sans redémarrer le bot
- **Base de Données** : SQLite avec données détaillées pour Hunt Royal

## 🚀 Installation et Configuration

### 1. Structure des Fichiers

```
Arsenal_bot/
├── modules/
│   ├── hunt_royal_system.py      # Module Hunt Royal complet
│   └── suggestions_system.py     # Système de suggestions
├── core/
│   └── module_reloader.py        # Système de hot-reload
├── test_modules.py               # Script de test
└── main.py                       # Bot principal (modifié)
```

### 2. Dépendances

```bash
pip install discord.py sqlite3 asyncio
```

### 3. Configuration

Le système s'intègre automatiquement au bot principal. Aucune configuration supplémentaire requise.

## 🏹 Module Hunt Royal

### Commandes Disponibles

#### 📊 Informations
- `!hunt hunter <nom>` - Informations détaillées sur un chasseur
- `!hunt dungeon <nom>` - Informations détaillées sur un donjon  
- `!hunt equipment <nom>` - Informations sur un équipement
- `!hunt gem <nom>` - Informations sur une gemme

#### 🛠️ Outils d'Analyse
- `!hunt team <chasseur1> <chasseur2>...` - Analyser une composition d'équipe
- `!hunt recommend <donjon>` - Équipe recommandée pour un donjon
- `!hunt build <chasseur>` - Builds recommandés pour un chasseur
- `!hunt tier` - Tier list des chasseurs

#### 💡 Suggestions Hunt Royal
- `!hunt suggest <titre> | <description>` - Créer une suggestion Hunt Royal
- `!hunt vote <id> <up/down>` - Voter sur une suggestion
- `!hunt suggestions` - Voir les suggestions Hunt Royal

#### ⚙️ Gestion (Admin uniquement)
- `!hunt add hunter <données>` - Ajouter un chasseur
- `!hunt add dungeon <données>` - Ajouter un donjon
- `!hunt reload` - Recharger le module Hunt Royal

### Exemples d'utilisation

```bash
# Voir les infos d'un chasseur
!hunt hunter raven

# Analyser une équipe
!hunt team raven flamewarden frostguard

# Voir les infos d'un donjon
!hunt dungeon shadow temple

# Créer une suggestion
!hunt suggest Nouveau chasseur | Il faudrait ajouter un chasseur de type Vent avec des capacités de support
```

## 💡 Système de Suggestions

### Commandes Générales

#### 📝 Créer des Suggestions
- `!suggest <titre> | <description>` - Suggestion basique
- `!suggest advanced` - Mode interactif
- `!suggest hunt <suggestion>` - Suggestion Hunt Royal spécifique

#### 🗳️ Gestion des Suggestions
- `!suggest list` - Voir toutes les suggestions
- `!suggest my` - Mes suggestions
- `!suggest top` - Top des suggestions les mieux votées
- `!suggest status <id>` - État d'une suggestion

#### ⚙️ Administration
- `!suggest approve <id>` - Approuver une suggestion
- `!suggest reject <id> <raison>` - Rejeter une suggestion
- `!suggest implement <id>` - Marquer comme implémentée
- `!suggest stats` - Statistiques des suggestions

### Catégories Automatiques

Le système détecte automatiquement la catégorie basée sur le contenu :

- **hunt_royal** : Mots-clés Hunt Royal
- **bot** : Améliorations du bot Discord
- **music** : Système de musique
- **moderation** : Outils de modération
- **bug** : Signalement de bugs
- **feature** : Nouvelles fonctionnalités

## 🔄 Système de Hot-Reload

### Commandes de Gestion

#### 📋 Information
- `!module list` - Lister tous les modules
- `!module status` - État détaillé des modules
- `!module logs` - Logs de rechargement

#### 🔄 Rechargement
- `!module reload <nom>` - Recharger un module spécifique
- `!module load <nom>` - Charger un module
- `!module unload <nom>` - Décharger un module
- `!module scan` - Rescanner les modules

#### 🏹 Modules Spéciaux
- `!module reload hunt_royal_system` - Recharger Hunt Royal
- `!module reload suggestions_system` - Recharger les suggestions

### Auto-Reload

Le système surveille automatiquement les modifications dans :
- `modules/` - Modules personnalisés
- `commands/` - Commandes du bot
- `core/` - Fonctions essentielles
- `utils/` - Utilitaires

## 🗄️ Base de Données

### Hunt Royal Database

**Tables principales :**
- `hunters` - Chasseurs avec stats complètes
- `dungeons` - Donjons avec boss et stratégies
- `equipment` - Équipements avec bonus et sets
- `gems` - Gemmes avec effets spéciaux
- `builds` - Builds recommandés

**Données incluses :**
- 3+ chasseurs avec stats détaillées
- 2+ donjons avec stratégies
- Équipements légendaires et épiques
- Gemmes avec effets spéciaux

### Suggestions Database

**Tables principales :**
- `suggestions` - Suggestions avec votes
- `suggestion_votes` - Système de votes
- `suggestion_comments` - Commentaires
- `suggestion_categories` - Catégories personnalisées
- `suggestion_rewards` - Système de récompenses

## 🧪 Tests et Débogage

### Script de Test

```bash
python test_modules.py
```

Ce script teste :
- ✅ Imports des modules
- ✅ Création des bases de données
- ✅ Scan des modules
- ✅ Données Hunt Royal

### Résolution de Problèmes

#### Erreur de Module Non Trouvé
```bash
# Vérifier la structure des dossiers
!module scan
!module list
```

#### Base de Données Corrompue
```bash
# Supprimer et recréer
!module reload hunt_royal_system
```

#### Module en Erreur
```bash
# Voir les logs détaillés
!module logs
!module status
```

## 📊 Statistiques et Monitoring

### Commandes de Monitoring
- `!hunt stats` - Statistiques Hunt Royal
- `!suggest stats` - Statistiques suggestions
- `!module status` - État des modules

### Logs Disponibles
- Rechargement de modules
- Créations de suggestions
- Votes et interactions
- Erreurs et exceptions

## 🔧 Personnalisation

### Ajouter des Chasseurs Hunt Royal

```python
# Dans hunt_royal_system.py, modifier hunters_data
{
    "id": "nouveau_chasseur",
    "name": "Nouveau Chasseur",
    "rarity": "Legendary",
    "element": "Wind",
    "weapon_type": "Bow",
    "attack_base": 1300,
    "health_base": 2600,
    "defense_base": 700,
    "speed_base": 900,
    # ... autres propriétés
}
```

### Ajouter des Catégories de Suggestions

```python
# Dans suggestions_system.py, modifier default_categories
('nouvelle_cat', 'Nouvelle Catégorie', 'Description', '🆕', '#color', False, False)
```

### Personnaliser les Répertoires Surveillés

```python
# Dans module_reloader.py, modifier watched_directories
self.watched_directories = [
    "modules/",
    "commands/", 
    "core/",
    "utils/",
    "custom/"  # Nouveau répertoire
]
```

## 🚨 Sécurité

### Permissions Requises

- **Hunt Royal** : Tous les utilisateurs
- **Suggestions** : Tous les utilisateurs (création), Admin (gestion)
- **Module Reload** : Administrateur uniquement

### Limitations

- Auto-reload : 5 secondes entre vérifications
- Suggestions : 1000 caractères max pour la description
- Votes : 1 vote par utilisateur par suggestion

## 📈 Performances

### Optimisations Incluses

- ✅ Cache des modules en mémoire
- ✅ Requêtes SQL optimisées
- ✅ Limitation des embeds Discord
- ✅ Gestion d'erreurs robuste

### Monitoring Recommandé

- Surveiller la taille des bases de données
- Vérifier les logs de rechargement
- Monitorer l'utilisation mémoire

## 🤝 Contribution

Pour contribuer au système :

1. **Nouvelles données Hunt Royal** : Modifier les données dans `hunt_royal_system.py`
2. **Nouvelles fonctionnalités** : Créer un nouveau module dans `modules/`
3. **Corrections** : Utiliser le système de suggestions intégré

## 📞 Support

En cas de problème :

1. Exécuter `python test_modules.py`
2. Vérifier `!module status`
3. Consulter `!module logs`
4. Créer une suggestion avec `!suggest`

---

**🏹 Hunt Royal System - Arsenal Bot V4**  
*Système complet pour guides de jeu et gestion de communauté*
