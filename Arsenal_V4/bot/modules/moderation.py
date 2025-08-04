"""
🛡️ Arsenal V4 - Module Modération
=================================

Système de modération complet avec auto-modération
"""

import discord
from discord.ext import commands
import asyncio
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List

class ModerationModule(commands.Cog):
    """Module de modération pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Configuration auto-modération
        self.automod_config = {
            'bad_words': [
                'spam', 'hack', 'scam', 'virus', 'malware',
                'phishing', 'token', 'nitro free', 'discord.gg/nitro'
            ],
            'max_mentions': 5,
            'max_emojis': 10,
            'caps_percentage': 70,
            'spam_detection': {
                'max_messages': 5,
                'time_window': 10  # secondes
            }
        }
        
        # Historique des messages pour détection de spam
        self.message_history = {}
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-modération des messages"""
        if message.author.bot or not message.guild:
            return
        
        # Vérifier si l'auto-modération est activée
        guild_config = self.get_guild_config(message.guild.id)
        if not guild_config.get('auto_mod', True):
            return
        
        # Ignorer les modérateurs
        if message.author.guild_permissions.manage_messages:
            return
        
        violations = []
        
        # Vérification des mots interdits
        if self.check_bad_words(message.content):
            violations.append("Langage inapproprié")
        
        # Vérification des mentions excessives
        if len(message.mentions) > self.automod_config['max_mentions']:
            violations.append(f"Trop de mentions ({len(message.mentions)})")
        
        # Vérification des emojis excessifs
        emoji_count = len(re.findall(r'<:[^:]+:\d+>', message.content))
        if emoji_count > self.automod_config['max_emojis']:
            violations.append(f"Trop d'emojis ({emoji_count})")
        
        # Vérification des majuscules excessives
        if self.check_excessive_caps(message.content):
            violations.append("Trop de majuscules")
        
        # Détection de spam
        if self.check_spam(message):
            violations.append("Spam détecté")
        
        # Traitement des violations
        if violations:
            await self.handle_violations(message, violations)
    
    def check_bad_words(self, content: str) -> bool:
        """Vérifier les mots interdits"""
        content_lower = content.lower()
        return any(word in content_lower for word in self.automod_config['bad_words'])
    
    def check_excessive_caps(self, content: str) -> bool:
        """Vérifier les majuscules excessives"""
        if len(content) < 10:  # Ignorer les messages courts
            return False
        
        caps_count = sum(1 for char in content if char.isupper())
        caps_percentage = (caps_count / len(content)) * 100
        
        return caps_percentage > self.automod_config['caps_percentage']
    
    def check_spam(self, message) -> bool:
        """Détecter le spam"""
        user_id = message.author.id
        now = datetime.now()
        
        # Initialiser l'historique pour cet utilisateur
        if user_id not in self.message_history:
            self.message_history[user_id] = []
        
        # Ajouter le message actuel
        self.message_history[user_id].append(now)
        
        # Nettoyer les anciens messages
        time_window = self.automod_config['spam_detection']['time_window']
        cutoff_time = now - timedelta(seconds=time_window)
        self.message_history[user_id] = [
            msg_time for msg_time in self.message_history[user_id]
            if msg_time > cutoff_time
        ]
        
        # Vérifier si l'utilisateur spamme
        max_messages = self.automod_config['spam_detection']['max_messages']
        return len(self.message_history[user_id]) > max_messages
    
    async def handle_violations(self, message, violations: List[str]):
        """Traiter les violations de modération"""
        try:
            # Supprimer le message
            await message.delete()
            
            # Avertir l'utilisateur
            embed = discord.Embed(
                title="⚠️ Message supprimé",
                description=f"{message.author.mention}, votre message a été supprimé.",
                color=0xff4757
            )
            
            embed.add_field(
                name="Violations détectées",
                value="• " + "\n• ".join(violations),
                inline=False
            )
            
            warning_msg = await message.channel.send(embed=embed)
            
            # Supprimer le message d'avertissement après 10 secondes
            await asyncio.sleep(10)
            try:
                await warning_msg.delete()
            except:
                pass
            
            # Ajouter un avertissement en base
            await self.add_warning(message.author.id, message.guild.id, 
                                 self.bot.user.id, f"Auto-mod: {', '.join(violations)}")
            
            # Vérifier si l'utilisateur doit être sanctionné
            warnings_count = self.get_user_warnings(message.author.id, message.guild.id)
            
            if warnings_count >= 3:
                await self.auto_mute(message.author, message.guild, "Trop d'avertissements")
            
        except Exception as e:
            print(f"Erreur handle_violations: {e}")
    
    @commands.command(name='warn', aliases=['avertir'])
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée"):
        """⚠️ Avertir un utilisateur"""
        
        if member == ctx.author:
            return await ctx.send("❌ Vous ne pouvez pas vous avertir vous-même !")
        
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Vous ne pouvez pas avertir ce membre !")
        
        # Ajouter l'avertissement
        await self.add_warning(member.id, ctx.guild.id, ctx.author.id, reason)
        warnings_count = self.get_user_warnings(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title="⚠️ Avertissement donné",
            description=f"{member.mention} a reçu un avertissement",
            color=0xffaa00
        )
        
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="Total d'avertissements", value=f"{warnings_count}/3", inline=True)
        
        if warnings_count >= 3:
            embed.add_field(
                name="⚠️ Action automatique",
                value="L'utilisateur sera automatiquement mute pour excès d'avertissements.",
                inline=False
            )
            await self.auto_mute(member, ctx.guild, "3 avertissements atteints")
        
        await ctx.send(embed=embed)
        
        # Notifier l'utilisateur en privé
        try:
            dm_embed = discord.Embed(
                title=f"⚠️ Avertissement sur {ctx.guild.name}",
                description=f"Vous avez reçu un avertissement.",
                color=0xffaa00
            )
            dm_embed.add_field(name="Raison", value=reason, inline=False)
            dm_embed.add_field(name="Modérateur", value=ctx.author.display_name, inline=True)
            dm_embed.add_field(name="Avertissements", value=f"{warnings_count}/3", inline=True)
            
            await member.send(embed=dm_embed)
        except:
            pass  # Ignorer si les DM sont fermés
    
    @commands.command(name='warnings', aliases=['avertissements'])
    async def show_warnings(self, ctx, member: discord.Member = None):
        """📋 Voir les avertissements d'un utilisateur"""
        
        target = member or ctx.author
        
        warnings = self.get_user_warnings_detailed(target.id, ctx.guild.id)
        
        if not warnings:
            embed = discord.Embed(
                title=f"📋 Avertissements de {target.display_name}",
                description="Aucun avertissement !",
                color=0x00ff41
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title=f"📋 Avertissements de {target.display_name}",
            description=f"Total: **{len(warnings)}** avertissements",
            color=0xffaa00
        )
        
        for i, warning in enumerate(warnings[-5:], 1):  # Afficher les 5 derniers
            moderator = ctx.guild.get_member(warning['moderator_id'])
            mod_name = moderator.display_name if moderator else "Modérateur inconnu"
            
            embed.add_field(
                name=f"Avertissement #{i}",
                value=f"**Raison:** {warning['reason']}\n**Modérateur:** {mod_name}\n**Date:** {warning['timestamp'][:19]}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clearwarnings', aliases=['clearwarn'])
    @commands.has_permissions(administrator=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """🧹 Effacer tous les avertissements d'un utilisateur"""
        
        warnings_count = self.get_user_warnings(member.id, ctx.guild.id)
        
        if warnings_count == 0:
            return await ctx.send(f"❌ {member.display_name} n'a aucun avertissement !")
        
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM moderation_logs
                WHERE user_id = ? AND guild_id = ? AND action = 'warning'
            ''', (member.id, ctx.guild.id))
            conn.commit()
        
        embed = discord.Embed(
            title="🧹 Avertissements effacés",
            description=f"Tous les avertissements de {member.mention} ont été supprimés.",
            color=0x00ff41
        )
        
        embed.add_field(name="Avertissements supprimés", value=str(warnings_count), inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute_user(self, ctx, member: discord.Member, duration: str = "permanent", *, reason: str = "Aucune raison spécifiée"):
        """🔇 Mute un utilisateur"""
        
        if member == ctx.author:
            return await ctx.send("❌ Vous ne pouvez pas vous mute vous-même !")
        
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Vous ne pouvez pas mute ce membre !")
        
        # Obtenir ou créer le rôle Muted
        muted_role = await self.get_or_create_muted_role(ctx.guild)
        
        if muted_role in member.roles:
            return await ctx.send(f"❌ {member.display_name} est déjà mute !")
        
        try:
            await member.add_roles(muted_role)
            
            # Parser la durée
            mute_duration = self.parse_duration(duration)
            duration_text = duration if duration != "permanent" else "permanent"
            
            embed = discord.Embed(
                title="🔇 Utilisateur mute",
                description=f"{member.mention} a été mute",
                color=0xff4757
            )
            
            embed.add_field(name="Durée", value=duration_text, inline=True)
            embed.add_field(name="Raison", value=reason, inline=True)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de modération
            await self.log_moderation(member.id, ctx.guild.id, ctx.author.id, 'mute', 
                                    f"{reason} | Durée: {duration_text}")
            
            # Unmute automatique si durée spécifiée
            if mute_duration:
                await asyncio.sleep(mute_duration)
                if muted_role in member.roles:
                    await member.remove_roles(muted_role)
                    try:
                        await ctx.send(f"🔊 {member.mention} a été automatiquement unmute.")
                    except:
                        pass
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du mute: {e}")
    
    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute_user(self, ctx, member: discord.Member):
        """🔊 Unmute un utilisateur"""
        
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role or muted_role not in member.roles:
            return await ctx.send(f"❌ {member.display_name} n'est pas mute !")
        
        try:
            await member.remove_roles(muted_role)
            
            embed = discord.Embed(
                title="🔊 Utilisateur unmute",
                description=f"{member.mention} peut de nouveau parler",
                color=0x00ff41
            )
            
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de modération
            await self.log_moderation(member.id, ctx.guild.id, ctx.author.id, 'unmute', 
                                    "Unmute manuel")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'unmute: {e}")
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée"):
        """👢 Kick un utilisateur"""
        
        if member == ctx.author:
            return await ctx.send("❌ Vous ne pouvez pas vous kick vous-même !")
        
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Vous ne pouvez pas kick ce membre !")
        
        try:
            # Notifier l'utilisateur avant le kick
            try:
                dm_embed = discord.Embed(
                    title=f"👢 Kick de {ctx.guild.name}",
                    description=f"Vous avez été expulsé du serveur.",
                    color=0xff4757
                )
                dm_embed.add_field(name="Raison", value=reason, inline=False)
                dm_embed.add_field(name="Modérateur", value=ctx.author.display_name, inline=True)
                
                await member.send(embed=dm_embed)
            except:
                pass
            
            await member.kick(reason=reason)
            
            embed = discord.Embed(
                title="👢 Utilisateur kick",
                description=f"{member.display_name} a été expulsé",
                color=0xff4757
            )
            
            embed.add_field(name="Raison", value=reason, inline=True)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de modération
            await self.log_moderation(member.id, ctx.guild.id, ctx.author.id, 'kick', reason)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du kick: {e}")
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée"):
        """🔨 Ban un utilisateur"""
        
        if member == ctx.author:
            return await ctx.send("❌ Vous ne pouvez pas vous ban vous-même !")
        
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Vous ne pouvez pas ban ce membre !")
        
        try:
            # Notifier l'utilisateur avant le ban
            try:
                dm_embed = discord.Embed(
                    title=f"🔨 Ban de {ctx.guild.name}",
                    description=f"Vous avez été banni du serveur.",
                    color=0xff4757
                )
                dm_embed.add_field(name="Raison", value=reason, inline=False)
                dm_embed.add_field(name="Modérateur", value=ctx.author.display_name, inline=True)
                
                await member.send(embed=dm_embed)
            except:
                pass
            
            await member.ban(reason=reason)
            
            embed = discord.Embed(
                title="🔨 Utilisateur ban",
                description=f"{member.display_name} a été banni",
                color=0xff4757
            )
            
            embed.add_field(name="Raison", value=reason, inline=True)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log de modération
            await self.log_moderation(member.id, ctx.guild.id, ctx.author.id, 'ban', reason)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du ban: {e}")
    
    async def get_or_create_muted_role(self, guild) -> discord.Role:
        """Obtenir ou créer le rôle Muted"""
        muted_role = discord.utils.get(guild.roles, name="Muted")
        
        if not muted_role:
            # Créer le rôle
            muted_role = await guild.create_role(
                name="Muted",
                color=discord.Color(0x818386),
                reason="Rôle automatique pour les mutes"
            )
            
            # Configurer les permissions pour tous les canaux
            for channel in guild.channels:
                await channel.set_permissions(muted_role, 
                    send_messages=False,
                    speak=False,
                    add_reactions=False
                )
        
        return muted_role
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parser une durée (ex: 10m, 1h, 2d)"""
        if duration_str.lower() == "permanent":
            return None
        
        pattern = r'(\d+)([smhd])'
        match = re.match(pattern, duration_str.lower())
        
        if not match:
            return None
        
        value, unit = match.groups()
        value = int(value)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return value * multipliers[unit]
    
    async def add_warning(self, user_id: int, guild_id: int, moderator_id: int, reason: str):
        """Ajouter un avertissement"""
        await self.log_moderation(user_id, guild_id, moderator_id, 'warning', reason)
    
    def get_user_warnings(self, user_id: int, guild_id: int) -> int:
        """Compter les avertissements d'un utilisateur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM moderation_logs
                WHERE user_id = ? AND guild_id = ? AND action = 'warning'
            ''', (user_id, guild_id))
            
            return cursor.fetchone()[0]
    
    def get_user_warnings_detailed(self, user_id: int, guild_id: int) -> List[dict]:
        """Récupérer les détails des avertissements"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT moderator_id, reason, timestamp
                FROM moderation_logs
                WHERE user_id = ? AND guild_id = ? AND action = 'warning'
                ORDER BY timestamp DESC
            ''', (user_id, guild_id))
            
            warnings = cursor.fetchall()
            
            return [{
                'moderator_id': w[0],
                'reason': w[1],
                'timestamp': w[2]
            } for w in warnings]
    
    async def log_moderation(self, user_id: int, guild_id: int, moderator_id: int, action: str, reason: str):
        """Logger une action de modération"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO moderation_logs (guild_id, user_id, moderator_id, action, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, user_id, moderator_id, action, reason))
            conn.commit()
    
    async def auto_mute(self, member: discord.Member, guild: discord.Guild, reason: str):
        """Mute automatique"""
        try:
            muted_role = await self.get_or_create_muted_role(guild)
            await member.add_roles(muted_role)
            
            # Log
            await self.log_moderation(member.id, guild.id, self.bot.user.id, 'auto_mute', reason)
            
        except Exception as e:
            print(f"Erreur auto_mute: {e}")
    
    def get_guild_config(self, guild_id: int) -> dict:
        """Récupérer la configuration du serveur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT auto_mod, welcome_channel, logs_channel
                FROM guilds WHERE guild_id = ?
            ''', (guild_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'auto_mod': bool(result[0]),
                    'welcome_channel': result[1],
                    'logs_channel': result[2]
                }
            
            return {'auto_mod': True, 'welcome_channel': None, 'logs_channel': None}

def setup(bot):
    bot.add_cog(ModerationModule(bot))
