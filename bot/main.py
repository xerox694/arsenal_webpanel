"""
Arsenal Bot V4.2.1 - Main Entry Point
Bot Discord avec intégration WebPanel
"""

import discord
from discord.ext import commands, tasks
import asyncio
import os
import sys
import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports des modules bot
try:
    from bot.core.logger import info, error, warning, debug
    from bot.core.config import get_config, load_config
    from bot.core.status import update_bot_status
    print("[OK] Modules bot core importés")
except ImportError as e:
    print(f"[ERROR] Erreur import modules core: {e}")
    # Fallback basique
    def info(msg): print(f"[INFO] {msg}")
    def error(msg): print(f"[ERROR] {msg}")
    def warning(msg): print(f"[WARNING] {msg}")
    def debug(msg): print(f"[DEBUG] {msg}")
    def get_config(key, default=None): return default
    def load_config(): return {}
    def update_bot_status(**kwargs): pass

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    error("DISCORD_TOKEN non trouvé dans les variables d'environnement!")
    sys.exit(1)

info(f"Token Discord trouvé: {TOKEN[:20]}...")

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

class ArsenalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_config('general.prefix', '!'),
            intents=intents,
            help_command=None
        )
        self.startup_time = datetime.datetime.utcnow()
        
    async def setup_hook(self):
        """Hook appelé au démarrage du bot"""
        info("Configuration du bot...")
        
        # Démarrer les tâches de fond
        self.status_updater.start()
        self.activity_cycle.start()
        
        # Synchroniser les commandes slash
        try:
            synced = await self.tree.sync()
            info(f"Synchronisation réussie: {len(synced)} commandes")
        except Exception as e:
            error(f"Erreur synchronisation commandes: {e}")
    
    async def on_ready(self):
        """Événement quand le bot est prêt"""
        info(f"Bot connecté en tant que {self.user}")
        info(f"ID: {self.user.id}")
        info(f"Serveurs connectés: {len(self.guilds)}")
        
        # Mettre à jour le status
        update_bot_status(self)
        
        # Afficher les serveurs
        for guild in self.guilds:
            info(f"  - {guild.name} ({guild.id}) - {guild.member_count} membres")
    
    async def on_guild_join(self, guild):
        """Événement quand le bot rejoint un serveur"""
        info(f"Bot ajouté au serveur: {guild.name} ({guild.id})")
        update_bot_status(self)
    
    async def on_guild_remove(self, guild):
        """Événement quand le bot quitte un serveur"""
        info(f"Bot retiré du serveur: {guild.name} ({guild.id})")
        update_bot_status(self)
    
    @tasks.loop(minutes=5)
    async def status_updater(self):
        """Met à jour le statut du bot toutes les 5 minutes"""
        if self.is_ready():
            update_bot_status(self)
    
    @tasks.loop(seconds=30)
    async def activity_cycle(self):
        """Change l'activité du bot toutes les 30 secondes"""
        if not self.is_ready():
            return
            
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name="Arsenal V4.2.1"),
            discord.Activity(type=discord.ActivityType.listening, name=f"{len(self.guilds)} serveurs"),
            discord.Activity(type=discord.ActivityType.playing, name="WebPanel Dashboard"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{sum(g.member_count or 0 for g in self.guilds)} utilisateurs"),
        ]
        
        try:
            activity = activities[self.activity_cycle.current_loop % len(activities)]
            await self.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            debug(f"Erreur changement activité: {e}")

# Créer l'instance du bot
bot = ArsenalBot()

# Commandes de base
@bot.tree.command(name="ping", description="Teste la latence du bot")
async def ping(interaction: discord.Interaction):
    """Commande ping basique"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latence: {latency}ms",
        color=0x00ff00
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Informations sur le bot")
async def info_command(interaction: discord.Interaction):
    """Informations sur le bot"""
    uptime = datetime.datetime.utcnow() - bot.startup_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(
        title="🤖 Arsenal Bot V4.2.1",
        color=0x0099ff
    )
    embed.add_field(name="📊 Serveurs", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Utilisateurs", value=sum(g.member_count or 0 for g in bot.guilds), inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
    embed.add_field(name="🏓 Latence", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🌐 WebPanel", value="[Dashboard](https://arsenal-webpanel.onrender.com)", inline=True)
    embed.add_field(name="🐍 Python", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Statut détaillé du bot")
async def status_command(interaction: discord.Interaction):
    """Statut détaillé du bot"""
    try:
        # Informations système
        import psutil
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        embed = discord.Embed(
            title="📊 Statut Système",
            color=0x00ff00
        )
        embed.add_field(name="💾 RAM", value=f"{memory.percent}%", inline=True)
        embed.add_field(name="🖥️ CPU", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="📡 Réseau", value="✅ Connecté", inline=True)
        
    except ImportError:
        embed = discord.Embed(
            title="📊 Statut Bot",
            description="Système de monitoring non disponible",
            color=0xffaa00
        )
    
    await interaction.response.send_message(embed=embed)

# Gestionnaire d'erreurs
@bot.event
async def on_command_error(ctx, error):
    """Gestionnaire d'erreurs global"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignorer les commandes non trouvées
    
    error_msg = str(error)
    warning(f"Erreur commande: {error_msg}")
    
    try:
        await ctx.send(f"❌ Erreur: {error_msg}")
    except:
        pass

# Point d'entrée principal
if __name__ == "__main__":
    info("🚀 Démarrage Arsenal Bot V4.2.1...")
    
    try:
        # Charger la configuration
        load_config()
        info("Configuration chargée")
        
        # Mettre à jour le status initial
        update_bot_status(online=False, status="starting")
        
        # Démarrer le bot
        bot.run(TOKEN)
        
    except KeyboardInterrupt:
        info("Arrêt manuel du bot")
    except Exception as e:
        error(f"Erreur critique: {e}")
        update_bot_status(online=False, status="error")
    finally:
        info("Bot arrêté")
        update_bot_status(online=False, status="offline")
