# 🤖 Arsenal V4 - Bot Discord Complet

![Arsenal V4](https://img.shields.io/badge/Arsenal-V4-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge)
![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-purple?style=for-the-badge)

**Arsenal V4** est un bot Discord complet avec système économique, jeux, modération, musique et bien plus !

## 🌟 Fonctionnalités

### 💰 Système Économique
- **ArsenalCoins** - Monnaie virtuelle complète
- Commandes de travail avec cooldowns
- Récompenses quotidiennes
- Système de niveaux et XP
- Historique des transactions

### 🎮 Mini-Jeux
- **Roulette** - Pariez sur les couleurs et numéros
- **Coinflip** - Pile ou face avec multiplicateurs
- **Machines à sous** - Jackpots progressifs
- **Quiz** - Questions avec récompenses

### 🛒 Boutique
- Système de boutique configurable
- Catégories d'objets
- Inventaire personnel
- Rôles achetables
- Gestion des stocks

### 🛡️ Modération
- Auto-modération intelligente
- Système d'avertissements
- Mute/Ban/Kick avec raisons
- Logs de modération
- Détection de spam

### 🎵 Musique
- Lecture depuis YouTube
- Queue de musique
- Contrôles complets (pause, skip, volume)
- Playlists personnalisées
- Support multi-serveur

### 📊 Statistiques
- Stats détaillées par utilisateur
- Graphiques d'activité
- Leaderboards multiples
- Analytics du serveur
- Exportation de données

### 🎨 Personnalisation
- Profils utilisateur avec cartes
- Système de badges
- Thèmes personnalisables
- Avatars et arrière-plans
- Couleurs personnalisées

### ⚙️ Administration
- Panel d'admin complet
- Gestion base de données
- Mode maintenance
- Monitoring système
- Backup automatique

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- Un token de bot Discord
- FFmpeg (pour la musique)

### Installation locale

1. **Cloner le repository**
```bash
git clone https://github.com/votre-repo/arsenal-v4
cd arsenal-v4
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration**
Créez un fichier `.env` dans le dossier `bot/` :
```env
DISCORD_TOKEN=votre_token_discord
DATABASE_URL=./arsenal_v4.db
ENVIRONMENT=development
DEBUG=true
```

4. **Lancer le bot**
```bash
cd bot
python main.py
```

### Déploiement sur Render

1. **Fork ce repository**

2. **Créer un nouveau service sur Render**
   - Type: Worker
   - Repository: Votre fork
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot/main.py`

3. **Configurer les variables d'environnement**
   - `DISCORD_TOKEN`: Votre token Discord
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`

4. **Déployer**

## 📋 Commandes Principales

### 💰 Économie
- `!balance` - Voir votre solde
- `!work` - Travailler pour gagner des coins
- `!daily` - Récompense quotidienne
- `!pay @user montant` - Transférer des coins
- `!top coins` - Classement richesse

### 🎮 Jeux
- `!roulette` - Jouer à la roulette
- `!coinflip` - Pile ou face
- `!slots` - Machines à sous
- `!quiz` - Quiz avec récompenses

### 🛒 Boutique
- `!shop` - Voir la boutique
- `!buy objet` - Acheter un objet
- `!inventory` - Voir votre inventaire

### 🛡️ Modération
- `!warn @user raison` - Avertir un utilisateur
- `!mute @user durée` - Muter un utilisateur
- `!ban @user raison` - Bannir un utilisateur

### 🎵 Musique
- `!play chanson` - Jouer de la musique
- `!queue` - Voir la queue
- `!skip` - Passer la chanson
- `!volume 50` - Changer le volume

### 📊 Statistiques
- `!stats` - Stats du serveur
- `!profile @user` - Profil utilisateur
- `!leaderboard` - Classements

## 🔧 Configuration

### Structure de la base de données
Le bot utilise SQLite avec les tables :
- `users` - Données utilisateurs (balance, niveau, XP)
- `guilds` - Configuration serveurs
- `transactions` - Historique économique
- `inventory` - Inventaires utilisateurs
- `moderation_logs` - Logs de modération
- `daily_stats` - Statistiques quotidiennes
- `user_profiles` - Profils personnalisés

### Personnalisation
Vous pouvez modifier :
- **Économie** : Montants de récompenses dans `bot/modules/economy.py`
- **Jeux** : Probabilités et gains dans `bot/modules/games.py`
- **Boutique** : Objets disponibles dans `bot/modules/shop.py`
- **Badges** : Nouveaux badges dans `bot/modules/personalization.py`

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation** : [Wiki du projet](https://github.com/votre-repo/arsenal-v4/wiki)
- **Issues** : [Signaler un bug](https://github.com/votre-repo/arsenal-v4/issues)
- **Discord** : [Serveur de support](https://discord.gg/votre-serveur)

## 🏆 Fonctionnalités à venir

- [ ] Système de guildes/clans
- [ ] Événements automatiques
- [ ] API REST
- [ ] Interface web d'administration
- [ ] Intégration Twitch/YouTube
- [ ] Système de récompenses NFT
- [ ] Conversion ArsenalCoins vers cryptomonnaies

---

**Développé avec ❤️ par l'équipe Arsenal**

*Arsenal V4 - "Ouvrir une porte vers une ère nouvelle avec le bot"*
