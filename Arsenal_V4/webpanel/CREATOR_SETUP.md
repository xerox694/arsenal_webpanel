🔧 **CONFIGURATION CREATOR/ADMIN SETUP**

Pour finaliser le système de bypass creator, il faut:

## 1. Récupérer ton ID Discord
- Va sur Discord > Paramètres utilisateur > Avancé > Mode développeur (ON)
- Clique droit sur ton profil > "Copier l'ID"
- Ou tape `/id` dans n'importe quel channel

## 2. Modifier le fichier .env
```bash
# Configuration CREATOR/ADMIN (bypass tout)
CREATOR_ID=ton_id_discord_ici
ADMIN_IDS=ton_id_discord_ici,autre_admin_id
```

## 3. Redémarrer le serveur
```bash
python backend/app.py
```

## 4. Tester l'accès
- Va sur http://localhost:5000
- Connecte-toi avec Discord  
- Tu devrais avoir accès total en tant que "Créateur du Bot"

---

**Avantages du système Creator:**
✅ Bypass total de toutes les restrictions serveur
✅ Accès à toutes les fonctionnalités admin
✅ Niveau de permission maximum (1000)
✅ Marqué comme "Créateur du Bot" dans l'interface
✅ Accès à tous les serveurs Discord
