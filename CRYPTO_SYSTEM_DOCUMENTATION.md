# 💎 ARSENAL V4 - SYSTÈME CRYPTO & QR CODES

## 📋 Résumé du Système

Le système crypto d'Arsenal V4 permet aux utilisateurs de :
- **Convertir leurs ArsenalCoins en vraie cryptomonnaie ou euros**
- **Créer des QR codes pour transferts instantanés**
- **Envoyer et recevoir des ArsenalCoins via QR codes**
- **Gérer leurs portefeuilles crypto**

---

## 🏗️ Architecture du Système

### 📁 Fichiers Principaux

1. **`modules/crypto_system.py`**
   - Classe principale `CryptoSystem`
   - Génération de QR codes stylisés Arsenal
   - Gestion des transferts instantanés
   - Base de données crypto

2. **`commands/crypto_commands.py`**
   - Commandes Discord avec interface moderne
   - Modals et boutons interactifs
   - Intégration avec le système principal

3. **`crypto_bot_integration.py`**
   - Intégration dans le bot principal
   - Commandes classiques `!crypto`
   - Compatible avec l'architecture Arsenal

4. **`templates/crypto_qr.html`**
   - Interface web pour QR codes
   - Design Arsenal avec animations
   - API intégrée au webpanel

5. **`advanced_server.py`** (APIs ajoutées)
   - `/api/crypto/stats` - Statistiques utilisateur
   - `/api/crypto/wallets` - Gestion portefeuilles
   - `/api/crypto/create_transfer_qr` - Création QR
   - `/api/crypto/scan_qr` - Scanner QR codes
   - `/api/crypto/claim_transfer` - Réclamer transferts

---

## 🛠️ Installation & Configuration

### 1. Dépendances
```bash
pip install qrcode[pil] coinbase-wallet-sdk
```

### 2. Base de Données
Le système crée automatiquement :
- `crypto_wallets.db` - Portefeuilles utilisateurs
- Tables : `user_wallets`, `conversions`, `instant_transfers`, `qr_codes`

### 3. Configuration
Fichier `data/crypto_config.json` créé automatiquement avec :
```json
{
    "enabled": true,
    "min_conversion": 100,
    "max_conversion": 1000000,
    "commission_rate": 0.01,
    "instant_transfer_enabled": true,
    "qr_code_expiry_hours": 24,
    "supported_cryptos": ["ETH", "BTC", "BNB", "MATIC"],
    "coinbase_integration": true
}
```

---

## 💎 Fonctionnalités Principales

### 1. 📱 QR Codes Stylisés Arsenal
- **Design personnalisé** avec couleurs Arsenal (vert #00ff88)
- **Logo Arsenal intégré** dans chaque QR code
- **Expiration automatique** (1h pour transferts, 24h pour wallets)
- **Base64 encoding** pour envoi Discord/Web

### 2. 💸 Transferts Instantanés
- **Création QR** : `!crypto send 100`
- **Scan QR** : `!crypto scan transfer_123456`
- **Réclamation** : `!crypto claim 123`
- **Vérifications de sécurité** (solde, expiration, double-réclamation)

### 3. 💎 Gestion Portefeuilles
- **Support multi-crypto** : ETH, BTC, BNB, MATIC
- **Validation adresses** basique
- **QR codes pour adresses** de réception
- **Intégration Coinbase** (optionnelle)

### 4. 🔄 Système de Conversion
- **Taux fixe** : 1 ArsenalCoin = 0.01€
- **Commission** : 1% pour le propriétaire
- **Minimum** : 100 AC
- **Maximum** : 1M AC

---

## 🎮 Commandes Discord

### Commandes Principales
```bash
!crypto                    # Menu principal
!crypto wallet            # Voir portefeuilles
!crypto add ETH 0x...     # Ajouter portefeuille
!crypto send 100          # Créer QR transfert
!crypto scan <qr_id>      # Scanner QR code
!crypto claim <id>        # Réclamer transfert
!crypto stats             # Statistiques
!crypto help              # Aide complète
```

### Commandes Slash (Discord.py 2.0+)
```bash
/cryptowallet view        # Voir portefeuilles
/cryptowallet add         # Modal d'ajout
/cryptowallet qr          # Générer QR
/cryptosend 100           # Créer transfert
/cryptoscan <qr_id>       # Scanner QR
```

---

## 🌐 Interface Web

### Page principale : `/crypto-qr`
- **Dashboard crypto** avec statistiques
- **Génération QR codes** en temps réel
- **Scanner intégré** via input
- **Gestion portefeuilles** complète
- **Historique transferts** avec statuts

### APIs REST
```javascript
GET  /api/crypto/stats           // Statistiques utilisateur
GET  /api/crypto/wallets         // Liste portefeuilles
GET  /api/crypto/transfers       // Historique transferts
POST /api/crypto/create_transfer_qr // Créer QR transfert
POST /api/crypto/scan_qr         // Scanner QR code
POST /api/crypto/claim_transfer  // Réclamer transfert
POST /api/crypto/add_wallet      // Ajouter portefeuille
```

---

## 🔐 Sécurité & Validations

### Vérifications QR Codes
- **Expiration automatique** selon le type
- **Validation format** Arsenal unique
- **Prévention double-scan** pour transferts
- **Vérification solde** en temps réel

### Validations Transferts
- **Solde suffisant** avant création
- **Utilisateur authentifié** requis
- **Montant minimum** 10 AC
- **Pas d'auto-transfert** (même utilisateur)

### Protection Base de Données
- **Transactions SQLite** atomiques
- **Timestamps automatiques** sur toutes les opérations
- **Logs des actions** sensibles
- **Nettoyage QR expirés** automatique

---

## 📊 Base de Données Schema

### Table `user_wallets`
```sql
CREATE TABLE user_wallets (
    user_id INTEGER PRIMARY KEY,
    eth_address TEXT,
    btc_address TEXT,
    bnb_address TEXT,
    matic_address TEXT,
    coinbase_email TEXT,
    coinbase_wallet_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Table `instant_transfers`
```sql
CREATE TABLE instant_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    amount_ac INTEGER,
    qr_code_id TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    claimed_at TIMESTAMP
)
```

### Table `qr_codes`
```sql
CREATE TABLE qr_codes (
    id TEXT PRIMARY KEY,
    user_id INTEGER,
    type TEXT,  -- 'wallet_address' ou 'instant_transfer'
    data TEXT,  -- JSON avec données du QR
    amount_ac INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🚀 Intégration dans Arsenal V4

### 1. Dans `main.py`
```python
from crypto_bot_integration import setup_crypto_integration

# Après initialisation du bot
crypto_integration = setup_crypto_integration(bot)
```

### 2. Dans `advanced_server.py`
Les APIs crypto sont déjà intégrées dans le serveur principal.

### 3. Navigation WebPanel
Ajouter un lien vers `/crypto-qr` dans le menu principal.

---

## 🎯 Vision Révolutionnaire

Ce système permet à Arsenal V4 de devenir **le premier bot Discord** à :

1. **💰 Rémunérer réellement** ses utilisateurs
2. **🔗 Connecter Discord** à l'économie crypto
3. **📱 Démocratiser** les transferts crypto via QR codes
4. **🚀 Révolutionner** l'engagement communautaire

### Impact pour les utilisateurs :
- **Gains réels** en utilisant Discord normalement
- **Transferts instantanés** entre amis
- **Initiation crypto** en douceur
- **Nouvelle économie** communautaire

---

## 📋 TODO & Améliorations

### Phase 1 (Actuelle) ✅
- [x] Système QR codes fonctionnel
- [x] Transferts instantanés
- [x] Interface web complète
- [x] Commandes Discord
- [x] APIs REST

### Phase 2 (Prochaine)
- [ ] Validation adresses crypto avancée
- [ ] Intégration Coinbase API réelle
- [ ] Système de notifications push
- [ ] Mobile app pour scanner QR
- [ ] Analytics avancés

### Phase 3 (Future)
- [ ] Support NFTs
- [ ] Marketplace intégré
- [ ] Staking ArsenalCoins
- [ ] Partenariats exchanges
- [ ] API publique pour autres bots

---

## 🛟 Support & Maintenance

### Logs & Debug
Les logs sont automatiquement créés dans :
- Console du bot pour les erreurs crypto
- Base de données pour les transactions
- Fichiers de log rotatifs (optionnel)

### Nettoyage Automatique
```python
# Exécuté périodiquement
crypto_system.cleanup_expired_qr_codes()
```

### Monitoring
- Surveillance de l'utilisation CPU/RAM
- Alertes sur transactions suspectes
- Backup automatique des bases crypto

---

## 🎉 Conclusion

Le système crypto d'Arsenal V4 avec QR codes représente une **innovation majeure** dans l'écosystème Discord. Il transforme Arsenal d'un simple bot en une **plateforme économique révolutionnaire** où chaque interaction peut générer de la valeur réelle.

**Prêt à révolutionner Discord ? 🚀**
