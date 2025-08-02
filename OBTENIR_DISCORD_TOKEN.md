# 🤖 Comment obtenir ton DISCORD_TOKEN

## 1️⃣ Aller sur Discord Developer Portal
- Va sur : https://discord.com/developers/applications
- Connecte-toi avec ton compte Discord

## 2️⃣ Créer/Sélectionner ton Application Bot
- Si tu as déjà un bot : **Clique dessus**
- Sinon : **New Application** → Donner un nom → **Create**

## 3️⃣ Récupérer le Token
- Dans le menu à gauche : **Bot**
- Section **Token** : 
  - Si tu vois "Click to Reveal Token" → **Clique dessus**
  - Si tu vois "Reset Token" → **Reset Token** puis copie le nouveau
- **COPIE LE TOKEN** (commence par `MTM...` ou similaire)

## 4️⃣ Configurer sur Render
- Va sur render.com → Ton service `arsenal-webpanel`
- **Environment** tab
- **Add Environment Variable:**
  - Name: `DISCORD_TOKEN`
  - Value: `TON_TOKEN_COPIÉ_ICI`
- **Save Changes**

## 5️⃣ Redéploiement Automatique
- Render va automatiquement redéployer ton service
- Le bot Discord démarrera avec le WebPanel

## ⚠️ IMPORTANT :
- **NE PARTAGE JAMAIS** ton token Discord
- **NE LE METS PAS** dans le code source
- Il doit rester **secret** dans les variables d'environnement

## 🔍 Vérification :
Une fois ajouté, tu verras dans les logs Render :
```
🤖 Démarrage du bot Discord...
🚀 Bot process PID: [NUMERO]
✅ Bot connecté avec succès !
```
