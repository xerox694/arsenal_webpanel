# Arsenal V4 WebPanel - Service de ping externe
# Utilisez un service comme UptimeRobot (gratuit) ou cron-job.org

# 📋 Instructions:
# 1. Allez sur https://uptimerobot.com (gratuit)
# 2. Créez un compte
# 3. Ajoutez un nouveau monitor:
#    - Type: HTTP(s)
#    - URL: https://votre-app.onrender.com/health
#    - Interval: 5 minutes (minimum gratuit)
# 4. Votre app ne s'endormira plus jamais ! 🎯

# Alternative: cron-job.org
# 1. Allez sur https://cron-job.org
# 2. Créez un job qui ping votre URL toutes les 10 minutes
# 3. URL: https://votre-app.onrender.com/health

# 🚀 Bonus: Notification par email si l'app tombe en panne !

print("📌 N'oubliez pas de configurer UptimeRobot après le déploiement !")
print("URL à monitorer: https://[votre-app].onrender.com/health")
