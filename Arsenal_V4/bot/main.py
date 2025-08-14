#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 Arsenal V4 - Bot Discord Ultra Complet
====================================

Bot Discord avec système économique, modération, musique, jeux et bien plus !

Fonctionnalités principales :
- 🎮 Mini-jeux et système de niveaux XP
- 💰 Économie complète avec ArsenalCoins
- 🛠️ Modération automatique et manuelle
- 🎵 Système de musique avancé
- 📊 Statistiques et analytics
- 🎨 Personnalisation poussée
- 🌍 Fonctions communautaires

Author: Arsenal V4 Team
Version: 4.0.0
"""

import os
import sys
import asyncio
import logging
import aiohttp
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import sqlite3
import random
import math
from typing import Optional, Dict, List, Any

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('arsenal_v4.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('Arsenal_V4')

# Configuration du bot
class BotConfig:
    """Configuration centralisée du bot"""
    
    # Variables d'environnement
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # Base de données
    DATABASE_PATH = 'arsenal_v4.db'
    
    # Économie
    DEFAULT_BALANCE = 100
    DAILY_REWARD = 50
    WORK_COOLDOWN = 3600  # 1 heure
    WORK_REWARDS = (10, 50)  # Min, Max
    
    # XP et niveaux
    XP_PER_MESSAGE = (5, 15)
    XP_COOLDOWN = 60  # 1 minute
    
    # Modération
    AUTO_MOD_ENABLED = True
    MAX_WARNINGS = 3
    
    # Couleurs Discord
    COLORS = {
        'success': 0x00ff41,
        'error': 0xff4757,
        'warning': 0xffaa00,
        'info': 0x00fff7,
        'economy': 0xf39c12,
        'xp': 0xe74c3c
    }

class DatabaseManager:
    """Gestionnaire de base de données pour Arsenal V4"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données avec toutes les tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance INTEGER DEFAULT 100,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_daily TEXT,
                    last_work TEXT,
                    last_xp TEXT,
                    warnings INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table serveurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guilds (
                    guild_id INTEGER PRIMARY KEY,
                    name TEXT,
                    prefix TEXT DEFAULT '!',
                    auto_mod BOOLEAN DEFAULT 1,
                    welcome_channel INTEGER,
                    logs_channel INTEGER,
                    economy_enabled BOOLEAN DEFAULT 1,
                    xp_enabled BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table boutique
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shop_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    name TEXT,
                    description TEXT,
                    price INTEGER,
                    role_id INTEGER,
                    stock INTEGER DEFAULT -1,
                    category TEXT DEFAULT 'general',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table inventaire
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_inventory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    item_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    purchased_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, item_id)
                )
            ''')
            
            # Table logs de modération
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderation_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table transactions économiques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    amount INTEGER,
                    type TEXT,
                    description TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table jeux et statistiques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_stats (
                    user_id INTEGER,
                    guild_id INTEGER,
                    game_type TEXT,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    total_played INTEGER DEFAULT 0,
                    best_score INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id, game_type)
                )
            ''')
            
            conn.commit()
            logger.info("✅ Base de données initialisée avec succès")
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Récupérer ou créer un utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute('''
                    INSERT INTO users (user_id, username) 
                    VALUES (?, ?)
                ''', (user_id, f"User_{user_id}"))
                conn.commit()
                return self.get_user(user_id)
            
            return {
                'user_id': user[0],
                'username': user[1],
                'balance': user[2],
                'xp': user[3],
                'level': user[4],
                'last_daily': user[5],
                'last_work': user[6],
                'last_xp': user[7],
                'warnings': user[8],
                'created_at': user[9]
            }
    
    def update_balance(self, user_id: int, amount: int, description: str = ""):
        """Mettre à jour le solde d'un utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE user_id = ?
            ''', (amount, user_id))
            
            # Log de la transaction
            cursor.execute('''
                INSERT INTO transactions (user_id, amount, type, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount, 'balance_update', description))
            
            conn.commit()
    
    def add_xp(self, user_id: int, xp_amount: int):
        """Ajouter de l'XP et vérifier les montées de niveau"""
        user = self.get_user(user_id)
        new_xp = user['xp'] + xp_amount
        new_level = self.calculate_level(new_xp)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET xp = ?, level = ?, last_xp = ?
                WHERE user_id = ?
            ''', (new_xp, new_level, datetime.now().isoformat(), user_id))
            conn.commit()
        
        return new_level > user['level']  # True si level up
    
    @staticmethod
    def calculate_level(xp: int) -> int:
        """Calculer le niveau basé sur l'XP"""
        return int(math.sqrt(xp / 100)) + 1
    
    @staticmethod
    def xp_for_level(level: int) -> int:
        """XP nécessaire pour un niveau donné"""
        return (level - 1) ** 2 * 100

class ArsenalBot(commands.Bot):
    """Bot principal Arsenal V4"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        self.db = DatabaseManager(BotConfig.DATABASE_PATH)
        self.start_time = datetime.now()
        self.config = BotConfig()
        
        # Statistiques en temps réel
        self.stats = {
            'commands_executed': 0,
            'messages_processed': 0,
            'users_served': set(),
            'servers_count': 0
        }
    
    async def get_prefix(self, bot, message):
        """Préfixe dynamique par serveur"""
        if not message.guild:
            return BotConfig.PREFIX
        
        # TODO: Récupérer le préfixe depuis la DB par serveur
        return BotConfig.PREFIX
    
    async def on_ready(self):
        """Événement de démarrage du bot"""
        logger.info(f"🤖 {self.user} est connecté et prêt !")
        logger.info(f"📊 Connecté à {len(self.guilds)} serveurs")
        logger.info(f"👥 Servant {len(set(self.get_all_members()))} utilisateurs")
        
        # Mettre à jour les statistiques
        self.stats['servers_count'] = len(self.guilds)
        
        # Démarrer les tâches de fond
        self.update_status.start()
        
        # Synchroniser les commandes slash
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ {len(synced)} commandes slash synchronisées")
        except Exception as e:
            logger.error(f"❌ Erreur sync commandes slash: {e}")
    
    async def on_message(self, message):
        """Traitement des messages"""
        if message.author.bot:
            return
        
        self.stats['messages_processed'] += 1
        self.stats['users_served'].add(message.author.id)
        
        # Système d'XP
        if message.guild and BotConfig.XP_COOLDOWN:
            await self.process_xp(message)
        
        # Auto-modération
        if message.guild and BotConfig.AUTO_MOD_ENABLED:
            await self.auto_moderate(message)
        
        await self.process_commands(message)
    
    async def process_xp(self, message):
        """Traiter l'attribution d'XP"""
        user = self.db.get_user(message.author.id)
        
        # Vérifier le cooldown XP
        if user['last_xp']:
            last_xp_time = datetime.fromisoformat(user['last_xp'])
            if (datetime.now() - last_xp_time).seconds < BotConfig.XP_COOLDOWN:
                return
        
        # Attribuer XP et ArsenalCoins
        xp_gained = random.randint(*BotConfig.XP_PER_MESSAGE)
        coins_gained = random.randint(1, 3)
        
        level_up = self.db.add_xp(message.author.id, xp_gained)
        self.db.update_balance(message.author.id, coins_gained, "XP Message Reward")
        
        # Notification de level up
        if level_up:
            new_user = self.db.get_user(message.author.id)
            embed = discord.Embed(
                title="🎉 Level Up !",
                description=f"{message.author.mention} est maintenant niveau **{new_user['level']}** !",
                color=BotConfig.COLORS['xp']
            )
            embed.add_field(name="XP Total", value=f"{new_user['xp']:,}", inline=True)
            embed.add_field(name="Bonus Level Up", value=f"+{new_user['level'] * 10} ArsenalCoins", inline=True)
            
            # Bonus de level up
            self.db.update_balance(message.author.id, new_user['level'] * 10, f"Level {new_user['level']} Bonus")
            
            await message.channel.send(embed=embed)
    
    async def auto_moderate(self, message):
        """Auto-modération des messages"""
        content = message.content.lower()
        
        # Mots interdits basiques
        banned_words = ['spam', 'hack', 'scam']  # À étendre
        
        if any(word in content for word in banned_words):
            await message.delete()
            
            embed = discord.Embed(
                title="⚠️ Message supprimé",
                description="Votre message contenait du contenu interdit.",
                color=BotConfig.COLORS['warning']
            )
            
            await message.channel.send(embed=embed, delete_after=10)
    
    @tasks.loop(minutes=5)
    async def update_status(self):
        """Mettre à jour le statut du bot"""
        activities = [
            f"👥 {len(self.stats['users_served'])} utilisateurs",
            f"🏰 {self.stats['servers_count']} serveurs",
            f"⚡ {self.stats['commands_executed']} commandes",
            "🎮 Arsenal V4 | !help",
            "💰 ArsenalCoins Economy",
            "🎵 Musique et Fun"
        ]
        
        activity = discord.Game(random.choice(activities))
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_command(self, ctx):
        """Événement d'exécution de commande"""
        self.stats['commands_executed'] += 1
        logger.info(f"📝 Commande exécutée: {ctx.command} par {ctx.author} dans {ctx.guild}")

# Initialisation du bot
bot = ArsenalBot()

# ==================== COMMANDES ÉCONOMIE ====================

@bot.command(name='balance', aliases=['bal', 'money'])
async def balance(ctx, member: discord.Member = None):
    """Afficher le solde ArsenalCoins"""
    target = member or ctx.author
    user = bot.db.get_user(target.id)
    
    embed = discord.Embed(
        title=f"💰 Portefeuille de {target.display_name}",
        color=BotConfig.COLORS['economy']
    )
    
    embed.add_field(
        name="ArsenalCoins",
        value=f"🪙 **{user['balance']:,}** AC",
        inline=False
    )
    
    embed.add_field(
        name="Niveau",
        value=f"⭐ **{user['level']}** ({user['xp']:,} XP)",
        inline=True
    )
    
    # Prochain niveau
    next_level_xp = bot.db.xp_for_level(user['level'] + 1)
    embed.add_field(
        name="Prochain Niveau",
        value=f"📈 {next_level_xp - user['xp']:,} XP restants",
        inline=True
    )
    
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='daily')
async def daily(ctx):
    """Récompense quotidienne"""
    user = bot.db.get_user(ctx.author.id)
    
    # Vérifier si déjà réclamé aujourd'hui
    if user['last_daily']:
        last_daily = datetime.fromisoformat(user['last_daily'])
        if (datetime.now() - last_daily).days == 0:
            next_daily = last_daily + timedelta(days=1)
            time_left = next_daily - datetime.now()
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            
            embed = discord.Embed(
                title="⏰ Daily déjà réclamé",
                description=f"Revenez dans **{hours}h {minutes}m**",
                color=BotConfig.COLORS['warning']
            )
            return await ctx.send(embed=embed)
    
    # Donner la récompense
    reward = BotConfig.DAILY_REWARD
    bonus = user['level'] * 5  # Bonus basé sur le niveau
    total_reward = reward + bonus
    
    bot.db.update_balance(ctx.author.id, total_reward, "Daily Reward")
    
    # Mettre à jour la date du daily
    with sqlite3.connect(bot.db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET last_daily = ? WHERE user_id = ?',
            (datetime.now().isoformat(), ctx.author.id)
        )
        conn.commit()
    
    embed = discord.Embed(
        title="🎁 Récompense Quotidienne",
        description=f"Vous avez reçu **{total_reward:,}** ArsenalCoins !",
        color=BotConfig.COLORS['success']
    )
    
    embed.add_field(name="Récompense de base", value=f"{reward:,} AC", inline=True)
    embed.add_field(name="Bonus niveau", value=f"{bonus:,} AC", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='work')
async def work(ctx):
    """Travailler pour gagner des ArsenalCoins"""
    user = bot.db.get_user(ctx.author.id)
    
    # Vérifier le cooldown
    if user['last_work']:
        last_work = datetime.fromisoformat(user['last_work'])
        cooldown_time = BotConfig.WORK_COOLDOWN
        if (datetime.now() - last_work).seconds < cooldown_time:
            time_left = cooldown_time - (datetime.now() - last_work).seconds
            minutes, seconds = divmod(time_left, 60)
            
            embed = discord.Embed(
                title="😴 Vous êtes fatigué",
                description=f"Reposez-vous encore **{minutes}m {seconds}s**",
                color=BotConfig.COLORS['warning']
            )
            return await ctx.send(embed=embed)
    
    # Jobs disponibles
    jobs = [
        {"name": "Développeur Discord", "min": 20, "max": 50, "emoji": "💻"},
        {"name": "Modérateur", "min": 15, "max": 35, "emoji": "🛡️"},
        {"name": "Streamer", "min": 10, "max": 60, "emoji": "🎥"},
        {"name": "Designer", "min": 25, "max": 45, "emoji": "🎨"},
        {"name": "Musicien", "min": 30, "max": 40, "emoji": "🎵"},
        {"name": "Gamer Pro", "min": 15, "max": 55, "emoji": "🎮"}
    ]
    
    job = random.choice(jobs)
    earnings = random.randint(job["min"], job["max"])
    
    # Bonus de niveau
    level_bonus = user['level'] * 2
    total_earnings = earnings + level_bonus
    
    bot.db.update_balance(ctx.author.id, total_earnings, f"Work: {job['name']}")
    
    # Mettre à jour le timestamp de travail
    with sqlite3.connect(bot.db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET last_work = ? WHERE user_id = ?',
            (datetime.now().isoformat(), ctx.author.id)
        )
        conn.commit()
    
    embed = discord.Embed(
        title=f"{job['emoji']} Travail terminé !",
        description=f"Vous avez travaillé comme **{job['name']}**",
        color=BotConfig.COLORS['success']
    )
    
    embed.add_field(name="Gains", value=f"{earnings:,} AC", inline=True)
    embed.add_field(name="Bonus niveau", value=f"+{level_bonus:,} AC", inline=True)
    embed.add_field(name="Total", value=f"**{total_earnings:,}** ArsenalCoins", inline=True)
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if not BotConfig.TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN non défini dans les variables d'environnement")
        sys.exit(1)
    
    logger.info("🚀 Démarrage d'Arsenal V4...")
    bot.run(BotConfig.TOKEN)
