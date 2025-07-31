"""
🤖 Arsenal Bot Integration pour WebPanel
Intégration complète du bot Discord avec le panel web
"""
import discord
from discord.ext import commands
import asyncio
import aiohttp
import json
import sqlite3
from datetime import datetime
import sys
import os

# Configuration du bot
BOT_TOKEN = "VOTRE_TOKEN_BOT_ICI"  # À remplacer par votre vrai token
BOT_PREFIX = "!"

class ArsenalBot:
    def __init__(self):
        # Intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        # Initialisation du bot
        self.bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
        self.setup_events()
        self.setup_commands()
        
        # Base de données
        self.db_path = "arsenal_v4.db"
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données pour l'intégration bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour les logs de commandes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                username TEXT,
                command TEXT,
                server_id TEXT,
                server_name TEXT,
                timestamp DATETIME,
                success BOOLEAN
            )
        ''')
        
        # Table pour les statistiques en temps réel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_type TEXT,
                value INTEGER,
                timestamp DATETIME
            )
        ''')
        
        # Table pour les serveurs connectés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connected_servers (
                server_id TEXT PRIMARY KEY,
                server_name TEXT,
                member_count INTEGER,
                connected_at DATETIME,
                last_activity DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_events(self):
        """Configuration des événements du bot"""
        
        @self.bot.event
        async def on_ready():
            print(f'🤖 {self.bot.user} est connecté et prêt!')
            print(f'📊 Connecté à {len(self.bot.guilds)} serveurs')
            
            # Mettre à jour les statistiques
            await self.update_server_stats()
            
            # Démarrer la mise à jour automatique
            self.bot.loop.create_task(self.auto_update_stats())
        
        @self.bot.event
        async def on_guild_join(guild):
            """Quand le bot rejoint un serveur"""
            await self.add_server_to_db(guild)
            print(f'➕ Ajouté au serveur: {guild.name} ({guild.id})')
        
        @self.bot.event
        async def on_guild_remove(guild):
            """Quand le bot quitte un serveur"""
            await self.remove_server_from_db(guild.id)
            print(f'➖ Retiré du serveur: {guild.name} ({guild.id})')
        
        @self.bot.event
        async def on_command(ctx):
            """Log toutes les commandes exécutées"""
            await self.log_command(ctx, success=True)
        
        @self.bot.event
        async def on_command_error(ctx, error):
            """Log les erreurs de commandes"""
            await self.log_command(ctx, success=False)
            print(f'❌ Erreur commande: {error}')
    
    def setup_commands(self):
        """Configuration des commandes du bot"""
        
        @self.bot.command(name='play')
        async def play(ctx, *, query=None):
            """Commande pour jouer de la musique"""
            if not query:
                await ctx.send("❌ Veuillez spécifier une chanson à jouer!")
                return
            
            embed = discord.Embed(
                title="🎵 Musique",
                description=f"Recherche de: `{query}`",
                color=0x00ff88
            )
            await ctx.send(embed=embed)
            
            # Mettre à jour les stats
            await self.update_music_stats()
        
        @self.bot.command(name='skip')
        async def skip(ctx):
            """Passer la chanson actuelle"""
            embed = discord.Embed(
                title="⏭️ Musique",
                description="Chanson passée!",
                color=0x0088ff
            )
            await ctx.send(embed=embed)
        
        @self.bot.command(name='queue')
        async def queue(ctx):
            """Afficher la file d'attente"""
            embed = discord.Embed(
                title="📜 File d'attente",
                description="Aucune chanson en attente",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
        
        @self.bot.command(name='ban')
        @commands.has_permissions(ban_members=True)
        async def ban(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
            """Bannir un membre"""
            try:
                await member.ban(reason=reason)
                embed = discord.Embed(
                    title="🔨 Modération",
                    description=f"{member.mention} a été banni.\nRaison: {reason}",
                    color=0xff4444
                )
                await ctx.send(embed=embed)
                
                # Log dans la base de données
                await self.log_moderation_action("ban", member, ctx.author, reason)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur lors du bannissement: {e}")
        
        @self.bot.command(name='kick')
        @commands.has_permissions(kick_members=True)
        async def kick(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
            """Expulser un membre"""
            try:
                await member.kick(reason=reason)
                embed = discord.Embed(
                    title="👢 Modération",
                    description=f"{member.mention} a été expulsé.\nRaison: {reason}",
                    color=0xffaa00
                )
                await ctx.send(embed=embed)
                
                # Log dans la base de données
                await self.log_moderation_action("kick", member, ctx.author, reason)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de l'expulsion: {e}")
        
        @self.bot.command(name='panel')
        async def panel(ctx):
            """Lien vers le panel web"""
            embed = discord.Embed(
                title="🌐 Arsenal V4 Web Panel",
                description="Accédez au panel de contrôle web d'Arsenal!",
                color=0x00ff88
            )
            embed.add_field(
                name="Lien d'accès",
                value="[Cliquez ici pour accéder](http://localhost:8080)",
                inline=False
            )
            embed.add_field(
                name="Fonctionnalités",
                value="• Statistiques en temps réel\n• Gestion des serveurs\n• Logs des commandes\n• Contrôle musical",
                inline=False
            )
            await ctx.send(embed=embed)
        
        @self.bot.command(name='stats')
        async def stats(ctx):
            """Statistiques du bot"""
            stats = await self.get_bot_stats()
            
            embed = discord.Embed(
                title="📊 Statistiques Arsenal V4",
                color=0x00ff88
            )
            embed.add_field(name="Serveurs", value=stats['servers'], inline=True)
            embed.add_field(name="Utilisateurs", value=stats['users'], inline=True)
            embed.add_field(name="Commandes (24h)", value=stats['commands_24h'], inline=True)
            
            await ctx.send(embed=embed)
    
    async def log_command(self, ctx, success):
        """Log une commande dans la base de données"""
        try:
            # Log local dans SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO command_logs 
                (user_id, username, command, server_id, server_name, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(ctx.author.id),
                str(ctx.author),
                ctx.command.name if ctx.command else "unknown",
                str(ctx.guild.id) if ctx.guild else "DM",
                ctx.guild.name if ctx.guild else "Direct Message",
                datetime.now(),
                success
            ))
            
            conn.commit()
            conn.close()
            
            # Envoyer aussi au webpanel via API
            await self.send_to_webpanel({
                'user_id': str(ctx.author.id),
                'username': str(ctx.author),
                'command': ctx.command.name if ctx.command else "unknown",
                'server_id': str(ctx.guild.id) if ctx.guild else "DM",
                'server_name': ctx.guild.name if ctx.guild else "Direct Message",
                'success': success
            })
            
        except Exception as e:
            print(f"❌ Erreur log command: {e}")
    
    async def send_to_webpanel(self, data):
        """Envoyer des données au webpanel"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('http://localhost:5000/api/commands/log', json=data) as resp:
                    if resp.status == 200:
                        print(f"✅ Données envoyées au webpanel: {data['command']}")
                    else:
                        print(f"❌ Erreur webpanel: {resp.status}")
        except Exception as e:
            print(f"❌ Connexion webpanel échouée: {e}")
    
    async def update_server_stats_to_webpanel(self):
        """Envoyer les stats des serveurs au webpanel"""
        try:
            for guild in self.bot.guilds:
                server_data = {
                    'server_id': str(guild.id),
                    'server_name': guild.name,
                    'member_count': guild.member_count,
                    'connected_at': datetime.now().isoformat(),
                    'last_activity': datetime.now().isoformat()
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post('http://localhost:5000/api/servers/update', json=server_data) as resp:
                        if resp.status == 200:
                            print(f"✅ Stats serveur {guild.name} envoyées")
        except Exception as e:
            print(f"❌ Erreur stats serveurs: {e}")
    
    async def log_moderation_action(self, action_type, target, moderator, reason):
        """Log une action de modération"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO command_logs 
            (user_id, username, command, server_id, server_name, timestamp, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(target.id),
            f"{action_type}: {target} par {moderator}",
            action_type,
            str(target.guild.id),
            target.guild.name,
            datetime.now(),
            True
        ))
        
        conn.commit()
        conn.close()
    
    async def update_server_stats(self):
        """Mettre à jour les statistiques des serveurs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for guild in self.bot.guilds:
            cursor.execute('''
                INSERT OR REPLACE INTO connected_servers 
                (server_id, server_name, member_count, connected_at, last_activity)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(guild.id),
                guild.name,
                guild.member_count,
                datetime.now(),
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
    
    async def add_server_to_db(self, guild):
        """Ajouter un serveur à la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO connected_servers 
            (server_id, server_name, member_count, connected_at, last_activity)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            str(guild.id),
            guild.name,
            guild.member_count,
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    async def remove_server_from_db(self, guild_id):
        """Retirer un serveur de la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM connected_servers WHERE server_id = ?', (str(guild_id),))
        
        conn.commit()
        conn.close()
    
    async def update_music_stats(self):
        """Mettre à jour les statistiques musicales"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bot_stats (stat_type, value, timestamp)
            VALUES (?, ?, ?)
        ''', ("music_play", 1, datetime.now()))
        
        conn.commit()
        conn.close()
    
    async def get_bot_stats(self):
        """Récupérer les statistiques du bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Nombre de serveurs
        servers = len(self.bot.guilds)
        
        # Nombre total d'utilisateurs
        users = sum(guild.member_count for guild in self.bot.guilds)
        
        # Commandes des dernières 24h
        cursor.execute('''
            SELECT COUNT(*) FROM command_logs 
            WHERE timestamp > datetime('now', '-1 day')
        ''')
        commands_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'servers': servers,
            'users': users,
            'commands_24h': commands_24h
        }
    
    async def auto_update_stats(self):
        """Mise à jour automatique des statistiques"""
        while True:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                await self.update_server_stats()
                print("📊 Statistiques mises à jour")
            except Exception as e:
                print(f"❌ Erreur mise à jour stats: {e}")
    
    def run(self):
        """Démarrer le bot"""
        try:
            print("🚀 Démarrage du bot Arsenal V4...")
            self.bot.run(BOT_TOKEN)
        except Exception as e:
            print(f"❌ Erreur démarrage bot: {e}")
            print("💡 Vérifiez votre token Discord!")

# Point d'entrée
if __name__ == "__main__":
    arsenal_bot = ArsenalBot()
    arsenal_bot.run()
