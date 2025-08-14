# 🔑 Configuration Discord pour Arsenal V4 WebPanel

## 📋 **ÉTAPES POUR OBTENIR VOS CLÉS DISCORD**

### 1. **Aller sur Discord Developer Portal**
   - Allez sur: https://discord.com/developers/applications
   - Connectez-vous avec votre compte Discord

### 2. **Créer une Application Discord**
   - Cliquez sur "New Application"
   - Nom: "Arsenal V4 WebPanel"
   - Acceptez les conditions

### 3. **Récupérer les Clés**
   ```
   Dans "General Information":
   - CLIENT ID: Copiez l'Application ID
   - CLIENT SECRET: Cliquez "Reset Secret" et copiez
   ```

### 4. **Configurer OAuth2**
   ```
   Dans "OAuth2" > "General":
   - Redirect URIs: http://localhost:5000/auth/callback
   - Scopes: identify, guilds
   ```

### 5. **Créer un Bot Discord**
   ```
   Dans "Bot":
   - Cliquez "Add Bot"
   - BOT TOKEN: Cliquez "Reset Token" et copiez
   - Activez toutes les Privileged Gateway Intents
   ```

## 🔧 **MODIFIER VOTRE .ENV**

Éditez le fichier: `a:\Arsenal_bot\Arsenal_V4\webpanel\.env`

```env
# Remplacez ces valeurs par vos vraies clés:
DISCORD_CLIENT_ID=123456789012345678
DISCORD_CLIENT_SECRET=VotreCleSecrete_ABC123
DISCORD_BOT_TOKEN=MTAx.GH1234.VotreTokenBot_XYZ789
```

## 🚀 **APRÈS CONFIGURATION**

1. **Sauvegardez le .env**
2. **Redémarrez le serveur** (Ctrl+C puis relancer)
3. **Testez l'authentification Discord**

## ⚡ **TEST RAPIDE SANS DISCORD**

Si vous voulez tester l'interface MAINTENANT sans configurer Discord:

Accédez directement au dashboard:
**http://localhost:5000/dashboard**

## 🔍 **VÉRIFICATION ACTUELLE**

Le fichier .env existe avec des valeurs de test.
Pour une utilisation complète, remplacez:
- `YOUR_DISCORD_CLIENT_ID_HERE`
- `YOUR_DISCORD_CLIENT_SECRET_HERE` 
- `YOUR_BOT_TOKEN_HERE`

Par vos vraies clés Discord obtenues sur https://discord.com/developers/applications
