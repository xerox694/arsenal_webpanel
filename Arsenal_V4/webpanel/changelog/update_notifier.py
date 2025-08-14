"""
Système de notification pour les nouvelles versions Arsenal
Ce script peut être intégré au bot pour envoyer des notifications automatiques
"""

import discord
import json
import aiohttp
from datetime import datetime

class ArsenalUpdateNotifier:
    def __init__(self, bot):
        self.bot = bot
        self.version_info_url = "https://raw.githubusercontent.com/xerox3elite/arsenal-v4-webpanel/main/changelog/version_info.json"
    
    async def check_for_updates(self):
        """Vérifie s'il y a une nouvelle version disponible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.version_info_url) as response:
                    if response.status == 200:
                        version_data = await response.json()
                        return version_data
        except Exception as e:
            print(f"Erreur lors de la vérification des mises à jour: {e}")
        return None
    
    def create_update_embed(self, version_data):
        """Crée un embed Discord pour annoncer la mise à jour"""
        announcement = version_data.get("announcement", {})
        
        embed = discord.Embed(
            title=announcement.get("title", "🚀 Nouvelle version Arsenal disponible !"),
            description=announcement.get("description", "Une nouvelle version est disponible."),
            color=int(announcement.get("embed_color", "#00fff7").replace("#", ""), 16),
            timestamp=datetime.now()
        )
        
        # Ajouter les nouvelles fonctionnalités
        features = announcement.get("features", [])
        if features:
            features_text = "\n".join(features)
            embed.add_field(
                name="✨ Nouvelles Fonctionnalités",
                value=features_text,
                inline=False
            )
        
        # Ajouter les liens
        embed.add_field(
            name="📄 Changelog Complet",
            value=f"[Voir les détails]({version_data.get('changelog_url', '#')})",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Mise à Jour",
            value=f"[Redéployer]({version_data.get('deploy_url', '#')})",
            inline=True
        )
        
        embed.set_footer(
            text=announcement.get("footer", "Arsenal Bot"),
            icon_url="https://raw.githubusercontent.com/xerox3elite/arsenal-v4-webpanel/main/assets/arsenal_icon.png"
        )
        
        return embed
    
    async def notify_servers(self, version_data):
        """Envoie la notification à tous les serveurs (optionnel)"""
        embed = self.create_update_embed(version_data)
        
        for guild in self.bot.guilds:
            try:
                # Chercher un canal d'annonces ou général
                target_channel = None
                
                # Priorité aux canaux d'annonces
                for channel in guild.text_channels:
                    if any(word in channel.name.lower() for word in ["annonce", "news", "update", "général", "general"]):
                        if channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
                
                # Si aucun canal spécial, utiliser le premier canal disponible
                if not target_channel:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
                
                if target_channel:
                    await target_channel.send(embed=embed)
                    print(f"✅ Notification envoyée à {guild.name}")
                else:
                    print(f"❌ Aucun canal disponible sur {guild.name}")
                    
            except Exception as e:
                print(f"❌ Erreur envoi notification à {guild.name}: {e}")

# Exemple d'utilisation dans le bot
"""
# Dans votre fichier principal du bot:

from update_notifier import ArsenalUpdateNotifier

class ArsenalBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.update_notifier = ArsenalUpdateNotifier(self)
    
    async def on_ready(self):
        print(f'{self.user} est connecté!')
        
        # Vérifier les mises à jour au démarrage (optionnel)
        version_data = await self.update_notifier.check_for_updates()
        if version_data:
            print(f"Version actuelle: {version_data.get('current_version')}")

# Commande pour les administrateurs pour annoncer manuellement
@bot.command(name='announce_update')
@commands.has_permissions(administrator=True)
async def announce_update(ctx):
    version_data = await bot.update_notifier.check_for_updates()
    if version_data:
        embed = bot.update_notifier.create_update_embed(version_data)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Impossible de récupérer les informations de version.")
"""
