#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arsenal Bot - Système de Logs Configurables Ultra-Avancé
Inspiré de DraftBot mais en 10x mieux !
Auteur: xero3elite  
Version: 1.0.0 RÉVOLUTIONNAIRE
"""

import discord
from discord.ext import commands
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Union

class ArsenalLogsSystem:
    """
    Système de logs ultra-configurable pour Arsenal Bot
    Surpasse DraftBot en fonctionnalités et customisation
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "arsenal_logs_config.db"
        self.init_database()
        
        # 🔥 MODULES DE LOGS ULTRA-COMPLETS (Plus que DraftBot!)
        self.log_modules = {
            # === MODÉRATION & SÉCURITÉ ===
            "moderation": {
                "name": "🛡️ Modération",
                "description": "Sanctions, avertissements, timeouts",
                "events": ["member_ban", "member_unban", "member_kick", "member_timeout", "member_warn"],
                "color": 0xff4444,
                "emoji": "🛡️",
                "premium": False
            },
            "automod": {
                "name": "🤖 Auto-Modération", 
                "description": "Actions automatiques, filtres",
                "events": ["automod_spam", "automod_links", "automod_words", "automod_caps"],
                "color": 0xff8800,
                "emoji": "🤖",
                "premium": False
            },
            "security": {
                "name": "🔒 Sécurité",
                "description": "Tentatives de piratage, anti-raid",
                "events": ["raid_detected", "suspicious_activity", "mass_join", "anti_nuke"],
                "color": 0xcc0000,
                "emoji": "🔒",
                "premium": True
            },
            
            # === GESTION SERVEUR ===
            "server_config": {
                "name": "⚙️ Configuration",
                "description": "Modifications des paramètres serveur",
                "events": ["server_update", "role_create", "role_delete", "channel_create", "channel_delete"],
                "color": 0x5865f2,
                "emoji": "⚙️",
                "premium": False
            },
            "arrivals_departures": {
                "name": "🚪 Arrivées & Départs",
                "description": "Membres qui rejoignent/quittent",
                "events": ["member_join", "member_leave", "member_boost", "member_unboost"],
                "color": 0x00ff88,
                "emoji": "🚪",
                "premium": False
            },
            "channels": {
                "name": "💬 Salons",
                "description": "Création, suppression, modifications salons",
                "events": ["channel_create", "channel_delete", "channel_update", "thread_create"],
                "color": 0x7289da,
                "emoji": "💬",
                "premium": False
            },
            "roles": {
                "name": "👥 Rôles",
                "description": "Création, suppression, attribution rôles", 
                "events": ["role_create", "role_delete", "role_update", "member_role_add", "member_role_remove"],
                "color": 0x9b59b6,
                "emoji": "👥",
                "premium": False
            },
            
            # === CONTENU & CRÉATIF ===
            "emojis": {
                "name": "😀 Émojis",
                "description": "Ajout, suppression émojis/stickers",
                "events": ["emoji_create", "emoji_delete", "emoji_update"],
                "color": 0xf39c12,
                "emoji": "😀",
                "premium": False
            },
            "nicknames": {
                "name": "📝 Pseudos",
                "description": "Changements de pseudos/surnoms",
                "events": ["member_nick_change", "member_username_change"],
                "color": 0x3498db,
                "emoji": "📝",
                "premium": False
            },
            "stickers": {
                "name": "🎨 Autocollants",
                "description": "Gestion des stickers serveur",
                "events": ["sticker_create", "sticker_delete", "sticker_update"],
                "color": 0xe74c3c,
                "emoji": "🎨",
                "premium": False
            },
            
            # === ÉCONOMIE & GAMING ===
            "economy": {
                "name": "💰 Transactions",
                "description": "Système économique, transferts",
                "events": ["economy_transfer", "economy_daily", "economy_gamble", "shop_purchase"],
                "color": 0xf1c40f,
                "emoji": "💰",
                "premium": False
            },
            "levels": {
                "name": "📊 Niveaux",
                "description": "Gains XP, montées de niveau",
                "events": ["level_up", "xp_gain", "rank_change"],
                "color": 0x9b59b6,
                "emoji": "📊", 
                "premium": False
            },
            "gaming": {
                "name": "🎮 Gaming",
                "description": "Mini-jeux, tournois, achievements",
                "events": ["game_win", "tournament_join", "achievement_unlock"],
                "color": 0x00ff00,
                "emoji": "🎮",
                "premium": True
            },
            
            # === COMMUNICATION ===
            "voice": {
                "name": "🎤 Vocal",
                "description": "Connexions/déconnexions vocales",
                "events": ["voice_join", "voice_leave", "voice_move", "voice_mute"],
                "color": 0x1abc9c,
                "emoji": "🎤",
                "premium": False
            },
            "messages": {
                "name": "💬 Messages",
                "description": "Messages supprimés/modifiés",
                "events": ["message_delete", "message_edit", "message_bulk_delete"],
                "color": 0x95a5a6,
                "emoji": "💬",
                "premium": True
            },
            "events": {
                "name": "🎉 Événements",
                "description": "Événements serveur programmés",
                "events": ["event_create", "event_start", "event_end", "event_cancel"],
                "color": 0xff69b4,
                "emoji": "🎉",
                "premium": False
            },
            
            # === FONCTIONNALITÉS AVANCÉES ===
            "suggestions": {
                "name": "💡 Suggestions",
                "description": "Nouvelles suggestions, votes",
                "events": ["suggestion_create", "suggestion_approve", "suggestion_deny"],
                "color": 0xffaa00,
                "emoji": "💡",
                "premium": False
            },
            "custom_commands": {
                "name": "🔧 Commandes personnalisées",
                "description": "Utilisation commandes custom",
                "events": ["custom_command_use", "custom_command_create"],
                "color": 0x8e44ad,
                "emoji": "🔧",
                "premium": True
            },
            "threads": {
                "name": "🧵 Fils",
                "description": "Création/gestion des threads",
                "events": ["thread_create", "thread_delete", "thread_archive"],
                "color": 0x34495e,
                "emoji": "🧵",
                "premium": False
            },
            "integrations": {
                "name": "🔗 Intégrations",
                "description": "Webhooks, bots, intégrations",
                "events": ["webhook_create", "bot_add", "integration_update"],
                "color": 0x16a085,
                "emoji": "🔗",
                "premium": True
            },
            
            # === PREMIUM EXCLUSIF ===
            "boosters": {
                "name": "⭐ Boosters",
                "description": "Boosts serveur, nitro",
                "events": ["server_boost", "server_unboost", "boost_tier_change"],
                "color": 0xff73fa,
                "emoji": "⭐",
                "premium": True
            },
            "ai_moderation": {
                "name": "🧠 IA Modération",
                "description": "Modération par intelligence artificielle",
                "events": ["ai_toxic_detected", "ai_spam_prevented", "ai_threat_analyzed"],
                "color": 0x00ffff,
                "emoji": "🧠",
                "premium": True
            },
            "analytics": {
                "name": "📈 Analytics",
                "description": "Statistiques avancées serveur",
                "events": ["daily_stats", "weekly_report", "trend_analysis"],
                "color": 0x2ecc71,
                "emoji": "📈",
                "premium": True
            }
        }
    
    def init_database(self):
        """Initialiser la base de données des logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table configuration des logs par serveur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_config (
                guild_id TEXT,
                module_name TEXT,
                channel_id TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                color TEXT DEFAULT NULL,
                custom_format TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, module_name)
            )
        ''')
        
        # Table paramètres généraux par serveur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_settings (
                guild_id TEXT PRIMARY KEY,
                default_channel TEXT DEFAULT NULL,
                default_color TEXT DEFAULT '#cd6e57',
                ignored_channels TEXT DEFAULT '[]',
                ignored_users TEXT DEFAULT '[]',
                timestamp_format TEXT DEFAULT '%d/%m/%Y %H:%M:%S',
                language TEXT DEFAULT 'fr',
                premium_enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des logs stockés (pour audit)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                module_name TEXT,
                event_type TEXT,
                user_id TEXT,
                channel_id TEXT,
                content TEXT,
                embed_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données logs initialisée")

    async def get_guild_config(self, guild_id: int) -> Dict:
        """Récupérer la configuration d'un serveur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Configuration générale
        cursor.execute('SELECT * FROM logs_settings WHERE guild_id = ?', (str(guild_id),))
        settings = cursor.fetchone()
        
        if not settings:
            # Créer configuration par défaut
            cursor.execute('''
                INSERT INTO logs_settings (guild_id, default_color, premium_enabled)
                VALUES (?, ?, ?)
            ''', (str(guild_id), '#cd6e57', False))
            conn.commit()
            settings = (str(guild_id), None, '#cd6e57', '[]', '[]', '%d/%m/%Y %H:%M:%S', 'fr', False, datetime.now())
        
        # Configuration des modules
        cursor.execute('SELECT module_name, channel_id, enabled, color FROM logs_config WHERE guild_id = ?', (str(guild_id),))
        modules_config = {row[0]: {'channel_id': row[1], 'enabled': row[2], 'color': row[3]} for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'guild_id': guild_id,
            'default_channel': settings[1],
            'default_color': settings[2],
            'ignored_channels': json.loads(settings[3]),
            'ignored_users': json.loads(settings[4]),
            'timestamp_format': settings[5],
            'language': settings[6],
            'premium_enabled': bool(settings[7]),
            'modules': modules_config
        }

    async def set_module_channel(self, guild_id: int, module: str, channel_id: Optional[int] = None):
        """Configurer le salon pour un module"""
        if module not in self.log_modules:
            raise ValueError(f"Module '{module}' inexistant")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if channel_id:
            cursor.execute('''
                INSERT OR REPLACE INTO logs_config (guild_id, module_name, channel_id, enabled)
                VALUES (?, ?, ?, TRUE)
            ''', (str(guild_id), module, str(channel_id)))
        else:
            cursor.execute('DELETE FROM logs_config WHERE guild_id = ? AND module_name = ?', 
                         (str(guild_id), module))
        
        conn.commit()
        conn.close()

    def create_log_embed(self, module: str, event_type: str, data: Dict, guild_config: Dict) -> discord.Embed:
        """Créer un embed de log stylisé"""
        module_info = self.log_modules.get(module, {})
        
        # Couleur personnalisée ou par défaut
        color = guild_config.get('modules', {}).get(module, {}).get('color')
        if not color:
            color = module_info.get('color', int(guild_config.get('default_color', '#cd6e57').replace('#', ''), 16))
        
        embed = discord.Embed(
            title=f"{module_info.get('emoji', '📋')} {module_info.get('name', module.title())}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Contenu selon le type d'événement
        if event_type == "member_ban":
            embed.description = f"👨‍⚖️ **{data['user']}** a été banni"
            embed.add_field(name="Modérateur", value=data.get('moderator', 'Inconnu'), inline=True)
            embed.add_field(name="Raison", value=data.get('reason', 'Aucune raison'), inline=True)
            
        elif event_type == "member_join":
            embed.description = f"👋 **{data['user']}** a rejoint le serveur"
            embed.add_field(name="Compte créé", value=data.get('account_age', 'Inconnu'), inline=True)
            embed.add_field(name="Invité par", value=data.get('inviter', 'Lien permanent'), inline=True)
            
        elif event_type == "message_delete":
            embed.description = f"🗑️ Message supprimé dans {data.get('channel', 'salon inconnu')}"
            embed.add_field(name="Auteur", value=data.get('author', 'Inconnu'), inline=True)
            embed.add_field(name="Contenu", value=f"```{data.get('content', 'Contenu indisponible')[:1000]}```", inline=False)
            
        # Footer avec informations techniques
        embed.set_footer(text=f"Arsenal Bot • ID: {data.get('id', 'N/A')}")
        
        return embed

    async def log_event(self, guild_id: int, module: str, event_type: str, data: Dict):
        """Logger un événement"""
        guild_config = await self.get_guild_config(guild_id)
        
        # Vérifier si le module est configuré et activé
        module_config = guild_config['modules'].get(module)
        if not module_config or not module_config['enabled']:
            return
        
        channel_id = module_config.get('channel_id') or guild_config.get('default_channel')
        if not channel_id:
            return
        
        # Vérifier premium si nécessaire
        module_info = self.log_modules.get(module, {})
        if module_info.get('premium', False) and not guild_config.get('premium_enabled', False):
            return
        
        try:
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return
            
            embed = self.create_log_embed(module, event_type, data, guild_config)
            await channel.send(embed=embed)
            
            # Stocker dans l'historique
            self._store_log_history(guild_id, module, event_type, data, embed)
            
        except Exception as e:
            print(f"❌ Erreur envoi log: {e}")

    def _store_log_history(self, guild_id: int, module: str, event_type: str, data: Dict, embed: discord.Embed):
        """Stocker le log dans l'historique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs_history (guild_id, module_name, event_type, user_id, channel_id, content, embed_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(guild_id), module, event_type,
            str(data.get('user_id', '')), str(data.get('channel_id', '')),
            str(data.get('content', '')), embed.to_dict()
        ))
        
        conn.commit()
        conn.close()

# ==================== COMMANDES DISCORD ====================

class LogsCommands(commands.Cog):
    """Commandes pour configurer le système de logs"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logs_system = ArsenalLogsSystem(bot)

    @commands.group(name="logs", aliases=["log"])
    @commands.has_permissions(administrator=True)
    async def logs_config(self, ctx):
        """Configurer le système de logs Arsenal"""
        if ctx.invoked_subcommand is None:
            await self.show_logs_config(ctx)

    async def show_logs_config(self, ctx):
        """Afficher la configuration actuelle des logs (comme DraftBot)"""
        guild_config = await self.logs_system.get_guild_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="🔧 Configuration des Logs - Arsenal Bot",
            description="**Que souhaitez-vous configurer ?**",
            color=0x00fff7
        )
        
        # Informations générales
        default_channel = f"<#{guild_config['default_channel']}>" if guild_config['default_channel'] else "Aucun"
        embed.add_field(
            name="📋 Paramètres généraux",
            value=f"**Salon par défaut :** {default_channel}\n"
                  f"**Couleur par défaut :** {guild_config['default_color']}\n"
                  f"**Salons ignorés :** {len(guild_config['ignored_channels'])} salon(s)",
            inline=False
        )
        
        # Modules configurés (comme dans l'image DraftBot)
        modules_text = "**Modules configurés :**\n"
        
        for module_key, module_info in self.logs_system.log_modules.items():
            module_config = guild_config['modules'].get(module_key, {})
            enabled = module_config.get('enabled', False)
            channel_id = module_config.get('channel_id')
            
            status_emoji = "✅" if enabled and channel_id else "❌"
            premium_emoji = "⭐" if module_info.get('premium', False) else ""
            channel_text = f"<#{channel_id}>" if channel_id else "Non configuré"
            
            modules_text += f"{status_emoji} {premium_emoji}**{module_info['name']}** : {channel_text}\n"
        
        embed.add_field(name="📊 État des modules", value=modules_text, inline=False)
        
        # Footer avec infos premium
        premium_count = sum(1 for m in self.logs_system.log_modules.values() if m.get('premium', False))
        embed.set_footer(text=f"⭐ {premium_count} modules premium disponibles • Arsenal Bot")
        
        await ctx.send(embed=embed)

    @logs_config.command(name="salon", aliases=["channel"])
    async def set_log_channel(self, ctx, module: str, channel: discord.TextChannel = None):
        """Configurer le salon pour un module de logs"""
        if module not in self.logs_system.log_modules:
            available = ", ".join(self.logs_system.log_modules.keys())
            await ctx.send(f"❌ Module inexistant. Modules disponibles :\n```{available}```")
            return
        
        await self.logs_system.set_module_channel(ctx.guild.id, module, channel.id if channel else None)
        
        module_info = self.logs_system.log_modules[module]
        if channel:
            embed = discord.Embed(
                title="✅ Configuration mise à jour",
                description=f"Module **{module_info['name']}** configuré sur {channel.mention}",
                color=0x00ff88
            )
        else:
            embed = discord.Embed(
                title="✅ Configuration supprimée", 
                description=f"Module **{module_info['name']}** désactivé",
                color=0xff8800
            )
        
        await ctx.send(embed=embed)

def setup(bot):
    """Charger le système de logs"""
    bot.add_cog(LogsCommands(bot))
    print("🚀 Arsenal Logs System chargé - Système révolutionnaire activé !")
