import discord
from discord.ext import commands, tasks
import asyncio, os, sys, json, datetime, threading
from dotenv import load_dotenv

print(f"[DEBUG] Python path: {sys.path}")
print(f"[DEBUG] Working directory: {os.getcwd()}")
print(f"[DEBUG] Files in current dir: {os.listdir('.')[:10]}")

# Core config & logs
try:
    from core.logger import log
    print("[OK] [DEBUG] core.logger importé")
except Exception as e:
    print(f"[ERROR] [DEBUG] Erreur import core.logger: {e}")
    # Fallback logger
    import logging
    log = logging.getLogger(__name__)

try:
    from manager.config_manager import config_data, load_config, save_config
    print("[OK] [DEBUG] manager.config_manager importé")
except Exception as e:
    print(f"[ERROR] [DEBUG] Erreur import manager.config_manager: {e}")
    # Fallback config
    config_data = {}
    def load_config(): return {}
    def save_config(data): pass

def update_bot_status():
    """Met à jour le fichier de statut du bot pour l'API"""
    try:
        if hasattr(client, 'user') and client.user and client.is_ready():
            uptime_seconds = (datetime.datetime.utcnow() - client.startup_time).total_seconds()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime = f"{hours}h {minutes}m"
            
            status_data = {
                "online": True,
                "uptime": uptime,
                "latency": round(client.latency * 1000) if client.latency else 0,
                "servers_connected": len(client.guilds),
                "users_connected": sum(guild.member_count or 0 for guild in client.guilds),
                "status": "operational",
                "last_restart": client.startup_time.strftime("%H:%M:%S"),
                "last_update": datetime.datetime.utcnow().isoformat()
            }
        else:
            status_data = {
                "online": False,
                "uptime": "0h 0m",
                "latency": 0,
                "servers_connected": 0,
                "users_connected": 0,
                "status": "offline",
                "last_restart": "Jamais",
                "last_update": datetime.datetime.utcnow().isoformat()
            }
        
        with open('bot_status.json', 'w') as f:
            json.dump(status_data, f, indent=2)
        
    except Exception as e:
        print(f"[ERROR] Erreur update_bot_status: {e}")

# Système de rechargement de modules (NOUVEAU)
try:
    from core.module_reloader import ReloaderCommands, reload_group
    RELOADER_AVAILABLE = True
    print("[OK] Système de rechargement de modules chargé")
except Exception as e:
    RELOADER_AVAILABLE = False
    print(f"[WARNING] Système de rechargement non disponible: {e}")

# Modules Hunt Royal et Suggestions (NOUVEAU)
try:
    from modules.hunt_royal_system import HuntRoyalCommands
    from modules.suggestions_system import SuggestionsCommands
    HUNT_ROYAL_AVAILABLE = True
    SUGGESTIONS_AVAILABLE = True
    print("[OK] Modules Hunt Royal et Suggestions chargés")
except Exception as e:
    HUNT_ROYAL_AVAILABLE = False
    SUGGESTIONS_AVAILABLE = False
    print(f"[WARNING] Modules Hunt Royal/Suggestions non disponibles: {e}")

# Managers système & extension
from manager.voice_manager import restore_voice_channels
from manager.terminal_manager import start_terminal
from manager.memory_manager import memoire

# Setup audio
from commands.music import setup_audio

# Modules de commandes
import commands.creator_tools as creator
import commands.community as community
import commands.admin as admin
import commands.moderateur as moderateur
import commands.sanction as sanction
import commands.music as music

# WebPanel Integration Commands (NOUVEAU)
try:
    from commands.webpanel_integration import WebPanelCommands
    WEBPANEL_COMMANDS_AVAILABLE = True
    print("[OK] WebPanel Integration Commands chargé")
except Exception as e:
    WEBPANEL_COMMANDS_AVAILABLE = False
    print(f"[ERROR] Erreur import WebPanel Commands: {e}")

# Advanced Bot Features (NOUVEAU)
try:
    from commands.advanced_features import AdvancedBotFeatures
    ADVANCED_FEATURES_AVAILABLE = True
    print("[OK] Advanced Bot Features chargé")
except Exception as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"[ERROR] Erreur import Advanced Features: {e}")

# Hunt Royal Auth System (NOUVEAU)
try:
    import commands.hunt_royal_auth as hunt_auth
    HUNT_AUTH_AVAILABLE = True
    print("[OK] Hunt Royal Auth System chargé")
except Exception as e:
    HUNT_AUTH_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Auth non disponible: {e}")

# Hunt Royal Profiles System (NOUVEAU)
try:
    import commands.hunt_royal_profiles as hunt_profiles
    HUNT_PROFILES_AVAILABLE = True
    print("[OK] Hunt Royal Profiles System chargé")
except Exception as e:
    HUNT_PROFILES_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Profiles non disponible: {e}")

# Hunt Royal Integration System (NOUVEAU V4)
try:
    import commands.hunt_royal_integration as hunt_integration
    HUNT_INTEGRATION_AVAILABLE = True
    print("[OK] Hunt Royal Integration System chargé")
except Exception as e:
    HUNT_INTEGRATION_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Integration non disponible: {e}")

# Crypto System Integration (NOUVEAU V4.2)
try:
    from crypto_bot_integration import setup_crypto_integration
    CRYPTO_INTEGRATION_AVAILABLE = True
    print("[OK] Crypto System Integration chargé")
except Exception as e:
    CRYPTO_INTEGRATION_AVAILABLE = False
    print(f"[WARNING] Crypto System Integration non disponible: {e}")

# Panneau Creator GUI (Tkinter)
from gui.ArsenalCreatorStudio import lancer_creator_interface

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CREATOR_ID = int(os.getenv("CREATOR_ID", 431359112039890945))
PREFIX = os.getenv("PREFIX", "!")

# Vérification du token Discord
print("[INFO] Vérification des variables d'environnement...")
print(f"TOKEN présent: {'[OK] Oui' if TOKEN else '[ERROR] NON'}")
print(f"CREATOR_ID: {CREATOR_ID}")
print(f"PREFIX: {PREFIX}")

if not TOKEN:
    print("[ERROR] CRITIQUE: DISCORD_TOKEN manquant dans les variables d'environnement!")
    print("[INFO] Ajoutez DISCORD_TOKEN sur Render avec votre token de bot Discord")
    sys.exit(1)

intents = discord.Intents.all()

# Tâche de mise à jour du statut bot
@tasks.loop(seconds=30)
async def update_bot_status_task():
    """Met à jour le fichier de statut toutes les 30 secondes"""
    update_bot_status()

from discord import Activity, ActivityType, Streaming

async def cycle_status(bot):
    while not bot.is_ready():
        await asyncio.sleep(1)
    while True:
        stats = [
            Streaming(name="Arsenal Admin Studio", url="https://twitch.tv/xerox"),
            Activity(type=ActivityType.streaming, name=f"{sum(bot.command_usage.values())} commandes utilisées", url="https://twitch.tv/xerox"),
            Activity(type=ActivityType.watching, name=f"{len(os.listdir('.'))} dossiers, {sum(len(files) for _, _, files in os.walk('.'))} fichiers"),
            Activity(type=ActivityType.watching, name=f"{len(bot.guilds)} serveurs"),
            Activity(type=ActivityType.playing, name="Developed by XeRoX"),
        ]
        for act in stats:
            await bot.change_presence(activity=act)
            await asyncio.sleep(15)

class ArsenalBot(commands.Bot):
    async def setup_hook(self):
        # Ajoute ici les tâches de fond à lancer au démarrage
        self.loop.create_task(restore_voice_channels(self))
        self.loop.create_task(start_terminal(self))
        self.loop.create_task(cycle_status(self))
        setup_audio(self)
        
        # Charger le système de rechargement de modules
        if RELOADER_AVAILABLE:
            try:
                await self.add_cog(ReloaderCommands(self))
                log.info("[OK] Système de rechargement de modules chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement reloader: {e}")
        
        # Charger Hunt Royal et Suggestions
        if HUNT_ROYAL_AVAILABLE:
            try:
                await self.add_cog(HuntRoyalCommands(self))
                log.info("[OK] Module Hunt Royal chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Hunt Royal: {e}")
        
        if SUGGESTIONS_AVAILABLE:
            try:
                await self.add_cog(SuggestionsCommands(self))
                log.info("[OK] Module Suggestions chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Suggestions: {e}")
        
        # Charger Hunt Royal Integration
        if HUNT_INTEGRATION_AVAILABLE:
            try:
                await self.add_cog(hunt_integration.HuntRoyalIntegration(self))
                log.info("[OK] Module Hunt Royal Integration chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Hunt Royal Integration: {e}")
        
        # Charger Crypto System Integration
        if CRYPTO_INTEGRATION_AVAILABLE:
            try:
                self.crypto_integration = setup_crypto_integration(self)
                log.info("[OK] Module Crypto System Integration chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Crypto System Integration: {e}")
        
        # Charger WebPanel Integration Commands
        if WEBPANEL_COMMANDS_AVAILABLE:
            try:
                await self.add_cog(WebPanelCommands(self))
                log.info("[OK] Module WebPanel Integration Commands chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement WebPanel Commands: {e}")
        
        # Charger Advanced Bot Features
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                await self.add_cog(AdvancedBotFeatures(self))
                log.info("[OK] Module Advanced Bot Features chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Advanced Features: {e}")

client = ArsenalBot(command_prefix=PREFIX, intents=intents)
client.startup_time = datetime.datetime.utcnow()
client.command_usage = {}

@client.event
async def on_ready():
    streaming = discord.Streaming(
        name="Arsenal Admin Studio",
        url="https://www.twitch.tv/fakestream"
    )
    await client.change_presence(activity=streaming, status=discord.Status.online)
    print(f"{client.user} est prêt et en streaming !")
    log.info(f"[START] Arsenal Studio lancé comme {client.user.name}")
    try:
        await client.tree.sync()
        log.info(f"[SYNC] Commandes Slash synchronisées.")
        # Démarre le cycle de status ici
        if not hasattr(client, "status_task"):
            client.status_task = asyncio.create_task(cycle_status(client))
        # Démarre la mise à jour du statut du bot
        update_bot_status_task.start()
    except Exception as e:
        log.error(f"[SYNC ERROR] {e}")

# Imports modules
client.tree.add_command(moderateur.moderator_group)
client.tree.add_command(admin.admin_group)
client.tree.add_command(creator.creator_group)
client.tree.add_command(sanction.sanction_group)
client.tree.add_command(creator.creator_tools_group)

# Individuelles
client.tree.add_command(community.info)
client.tree.add_command(community.avatar)
client.tree.add_command(community.signaler_bug)
client.tree.add_command(community.vote)
client.tree.add_command(community.poll)
client.tree.add_command(community.magic_8ball)
client.tree.add_command(community.spin_wheel)
client.tree.add_command(community.top_vocal)
client.tree.add_command(community.top_messages)
client.tree.add_command(community.random_quote)
client.tree.add_command(community.leaderboard)
client.tree.add_command(community.version)

# Hunt Royal Auth Commands (NOUVEAU)
if HUNT_AUTH_AVAILABLE:
    client.tree.add_command(hunt_auth.register_hunt_royal)
    client.tree.add_command(hunt_auth.get_my_token)
    client.tree.add_command(hunt_auth.hunt_royal_stats)

# Hunt Royal Profile Commands (NOUVEAU)
if HUNT_PROFILES_AVAILABLE:
    client.tree.add_command(hunt_profiles.link_hunt_royal)
    client.tree.add_command(hunt_profiles.profile_hunt_royal)
    client.tree.add_command(hunt_profiles.unlink_hunt_royal)

# Reload System Commands (NOUVEAU)
if RELOADER_AVAILABLE:
    client.tree.add_command(reload_group)

# Creator GUI Panel
def lancer_gui():
    try:
        lancer_creator_interface(client)
    except Exception as e:
        log.warning(f"[GUI ERROR] {e}")

# Lancement
if __name__ == "__main__":
    import threading
    threading.Thread(target=lancer_gui, daemon=True).start()
    try:
        client.run(TOKEN)
    except Exception as e:
        log.error(f"[RUN ERROR] {e}")
