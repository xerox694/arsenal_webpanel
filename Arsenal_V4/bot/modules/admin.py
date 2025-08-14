"""
⚙️ Arsenal V4 - Module Administration
====================================

Système d'administration complet pour la gestion du bot et du serveur
"""

import discord
from discord.ext import commands
import sqlite3
import json
import asyncio
import os
import subprocess
import psutil
from datetime import datetime, timedelta
import sys
from typing import Optional, List, Dict

class AdminModule(commands.Cog):
    """Module d'administration pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.maintenance_mode = False
        self.authorized_users = [123456789]  # IDs des développeurs autorisés
    
    def is_authorized(self, user_id: int) -> bool:
        """Vérifier si l'utilisateur est autorisé pour les commandes admin"""
        return user_id in self.authorized_users
    
    @commands.group(name='admin', invoke_without_command=True)
    @commands.is_owner()
    async def admin(self, ctx):
        """⚙️ Commandes d'administration"""
        
        embed = discord.Embed(
            title="⚙️ Panel d'Administration Arsenal V4",
            description="Commandes disponibles pour l'administration du bot",
            color=0xff4757
        )
        
        embed.add_field(
            name="🔧 Système",
            value="`admin status` - Statut du bot\n`admin reload` - Recharger les modules\n`admin maintenance` - Mode maintenance",
            inline=False
        )
        
        embed.add_field(
            name="📊 Base de données",
            value="`admin db backup` - Sauvegarder la BDD\n`admin db stats` - Statistiques BDD\n`admin db clean` - Nettoyer la BDD",
            inline=False
        )
        
        embed.add_field(
            name="👥 Utilisateurs",
            value="`admin users top` - Top utilisateurs\n`admin users ban` - Bannir globalement\n`admin users reset` - Reset utilisateur",
            inline=False
        )
        
        embed.add_field(
            name="🏰 Serveurs",
            value="`admin guilds list` - Liste des serveurs\n`admin guilds leave` - Quitter un serveur\n`admin guilds stats` - Stats serveurs",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @admin.command(name='status')
    @commands.is_owner()
    async def admin_status(self, ctx):
        """📊 Statut détaillé du bot"""
        
        # Informations système
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()
        
        # Informations bot
        guilds_count = len(self.bot.guilds)
        users_count = sum(guild.member_count for guild in self.bot.guilds)
        
        # Uptime
        uptime = datetime.now() - self.bot.start_time if hasattr(self.bot, 'start_time') else timedelta(0)
        
        embed = discord.Embed(
            title="📊 Statut du Bot Arsenal V4",
            color=0x00ff41 if not self.maintenance_mode else 0xff4757
        )
        
        embed.add_field(
            name="🤖 Bot",
            value=f"**Statut:** {'🔧 Maintenance' if self.maintenance_mode else '🟢 En ligne'}\n**Uptime:** {str(uptime).split('.')[0]}\n**Ping:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="💻 Système",
            value=f"**RAM:** {memory_usage:.1f} MB\n**CPU:** {cpu_usage:.1f}%\n**Python:** {sys.version[:5]}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Statistiques",
            value=f"**Serveurs:** {guilds_count:,}\n**Utilisateurs:** {users_count:,}\n**Commandes:** {getattr(self.bot, 'commands_used', 0):,}",
            inline=True
        )
        
        # Modules chargés
        loaded_modules = [cog for cog in self.bot.cogs.keys()]
        embed.add_field(
            name="🧩 Modules chargés",
            value=", ".join(loaded_modules) if loaded_modules else "Aucun",
            inline=False
        )
        
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
    
    @admin.command(name='reload')
    @commands.is_owner()
    async def reload_modules(self, ctx, module: str = None):
        """🔄 Recharger les modules"""
        
        if module:
            # Recharger un module spécifique
            try:
                self.bot.reload_extension(f'modules.{module}')
                await ctx.send(f"✅ Module `{module}` rechargé avec succès !")
            except Exception as e:
                await ctx.send(f"❌ Erreur lors du rechargement de `{module}`: {e}")
        else:
            # Recharger tous les modules
            reloaded = []
            failed = []
            
            for extension in list(self.bot.extensions.keys()):
                try:
                    self.bot.reload_extension(extension)
                    reloaded.append(extension.split('.')[-1])
                except Exception as e:
                    failed.append(f"{extension.split('.')[-1]}: {e}")
            
            embed = discord.Embed(
                title="🔄 Rechargement des modules",
                color=0x00ff41 if not failed else 0xffaa00
            )
            
            if reloaded:
                embed.add_field(
                    name="✅ Rechargés",
                    value=", ".join(reloaded),
                    inline=False
                )
            
            if failed:
                embed.add_field(
                    name="❌ Échecs",
                    value="\n".join(failed[:5]),  # Limiter à 5 erreurs
                    inline=False
                )
            
            await ctx.send(embed=embed)
    
    @admin.command(name='maintenance')
    @commands.is_owner()
    async def maintenance_mode(self, ctx, action: str = None):
        """🔧 Gérer le mode maintenance"""
        
        if action and action.lower() in ['on', 'off']:
            self.maintenance_mode = action.lower() == 'on'
            
            status = "activé" if self.maintenance_mode else "désactivé"
            color = 0xff4757 if self.maintenance_mode else 0x00ff41
            
            embed = discord.Embed(
                title=f"🔧 Mode maintenance {status}",
                description="Le bot est maintenant en mode maintenance" if self.maintenance_mode else "Le bot est sorti du mode maintenance",
                color=color
            )
            
            await ctx.send(embed=embed)
            
            # Changer le statut du bot
            if self.maintenance_mode:
                await self.bot.change_presence(
                    status=discord.Status.dnd,
                    activity=discord.Activity(type=discord.ActivityType.watching, name="🔧 Maintenance")
                )
            else:
                await self.bot.change_presence(
                    status=discord.Status.online,
                    activity=discord.Game(name="Arsenal V4 | /help")
                )
        else:
            status = "activé" if self.maintenance_mode else "désactivé"
            await ctx.send(f"🔧 Mode maintenance actuellement: **{status}**\nUtilisez `admin maintenance on/off` pour changer")
    
    @admin.group(name='db', invoke_without_command=True)
    @commands.is_owner()
    async def database(self, ctx):
        """💾 Gestion de la base de données"""
        
        embed = discord.Embed(
            title="💾 Gestion Base de Données",
            description="Commandes disponibles pour la gestion de la BDD",
            color=0x3498db
        )
        
        embed.add_field(
            name="Commandes",
            value="`admin db backup` - Créer une sauvegarde\n`admin db stats` - Statistiques\n`admin db clean` - Nettoyer les données\n`admin db optimize` - Optimiser la BDD",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @database.command(name='backup')
    @commands.is_owner()
    async def db_backup(self, ctx):
        """💾 Sauvegarder la base de données"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"arsenal_backup_{timestamp}.db"
            backup_path = f"backups/{backup_name}"
            
            # Créer le dossier de sauvegarde s'il n'existe pas
            os.makedirs("backups", exist_ok=True)
            
            # Copier la base de données
            import shutil
            shutil.copy2(self.bot.db.db_path, backup_path)
            
            embed = discord.Embed(
                title="✅ Sauvegarde créée",
                description=f"Base de données sauvegardée: `{backup_name}`",
                color=0x00ff41
            )
            
            # Taille du fichier
            file_size = os.path.getsize(backup_path) / 1024 / 1024  # MB
            embed.add_field(name="Taille", value=f"{file_size:.2f} MB", inline=True)
            embed.add_field(name="Date", value=timestamp, inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la sauvegarde: {e}")
    
    @database.command(name='stats')
    @commands.is_owner()
    async def db_stats(self, ctx):
        """📊 Statistiques de la base de données"""
        
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Compter les enregistrements dans chaque table
            stats = {}
            
            tables = [
                'users', 'guilds', 'transactions', 'inventory', 
                'moderation_logs', 'daily_stats', 'member_events',
                'user_profiles'
            ]
            
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0
            
            # Taille de la base de données
            db_size = os.path.getsize(self.bot.db.db_path) / 1024 / 1024  # MB
        
        embed = discord.Embed(
            title="📊 Statistiques Base de Données",
            color=0x3498db
        )
        
        embed.add_field(
            name="📈 Enregistrements",
            value=f"**Utilisateurs:** {stats.get('users', 0):,}\n**Serveurs:** {stats.get('guilds', 0):,}\n**Transactions:** {stats.get('transactions', 0):,}",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Activité",
            value=f"**Modération:** {stats.get('moderation_logs', 0):,}\n**Stats journalières:** {stats.get('daily_stats', 0):,}\n**Événements:** {stats.get('member_events', 0):,}",
            inline=True
        )
        
        embed.add_field(
            name="👤 Personnalisation",
            value=f"**Profils:** {stats.get('user_profiles', 0):,}\n**Inventaires:** {stats.get('inventory', 0):,}",
            inline=True
        )
        
        embed.add_field(
            name="💾 Fichier",
            value=f"**Taille:** {db_size:.2f} MB\n**Chemin:** `{self.bot.db.db_path}`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @database.command(name='clean')
    @commands.is_owner()
    async def db_clean(self, ctx, days: int = 30):
        """🧹 Nettoyer les anciennes données"""
        
        if days < 7:
            return await ctx.send("❌ Minimum 7 jours pour la sécurité !")
        
        confirmation_msg = await ctx.send(f"⚠️ Êtes-vous sûr de vouloir supprimer les données de plus de {days} jours ? Réagissez avec ✅ pour confirmer.")
        await confirmation_msg.add_reaction("✅")
        await confirmation_msg.add_reaction("❌")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirmation_msg.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "❌":
                return await ctx.send("❌ Nettoyage annulé.")
            
            # Nettoyer les données
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.bot.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Supprimer les anciens logs de modération
                cursor.execute('''
                    DELETE FROM moderation_logs
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                mod_deleted = cursor.rowcount
                
                # Supprimer les anciennes stats journalières
                cursor.execute('''
                    DELETE FROM daily_stats
                    WHERE date < DATE(?, '-{} days')
                '''.format(days), (datetime.now().strftime('%Y-%m-%d'),))
                stats_deleted = cursor.rowcount
                
                # Supprimer les anciens événements
                cursor.execute('''
                    DELETE FROM member_events
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                events_deleted = cursor.rowcount
                
                conn.commit()
            
            embed = discord.Embed(
                title="🧹 Nettoyage terminé",
                description=f"Données de plus de {days} jours supprimées",
                color=0x00ff41
            )
            
            embed.add_field(
                name="📊 Supprimé",
                value=f"**Logs modération:** {mod_deleted:,}\n**Stats journalières:** {stats_deleted:,}\n**Événements:** {events_deleted:,}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps d'attente dépassé. Nettoyage annulé.")
    
    @admin.group(name='users', invoke_without_command=True)
    @commands.is_owner()
    async def users_admin(self, ctx):
        """👥 Gestion des utilisateurs"""
        
        embed = discord.Embed(
            title="👥 Gestion des Utilisateurs",
            description="Commandes pour gérer les utilisateurs du bot",
            color=0x3498db
        )
        
        embed.add_field(
            name="Commandes",
            value="`admin users top` - Top utilisateurs\n`admin users info <id>` - Info utilisateur\n`admin users ban <id>` - Ban global\n`admin users reset <id>` - Reset données",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @users_admin.command(name='top')
    @commands.is_owner()
    async def users_top(self, ctx, category: str = "balance"):
        """🏆 Top utilisateurs globaux"""
        
        valid_categories = ["balance", "level", "messages"]
        
        if category not in valid_categories:
            return await ctx.send(f"❌ Catégorie invalide ! Utilisez: {', '.join(valid_categories)}")
        
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            if category == "balance":
                cursor.execute('''
                    SELECT user_id, SUM(balance) as total_balance
                    FROM users
                    GROUP BY user_id
                    ORDER BY total_balance DESC
                    LIMIT 10
                ''')
            elif category == "level":
                cursor.execute('''
                    SELECT user_id, MAX(level) as max_level, MAX(xp) as max_xp
                    FROM users
                    GROUP BY user_id
                    ORDER BY max_level DESC, max_xp DESC
                    LIMIT 10
                ''')
            else:  # messages
                cursor.execute('''
                    SELECT user_id, SUM(message_count) as total_messages
                    FROM daily_stats
                    GROUP BY user_id
                    ORDER BY total_messages DESC
                    LIMIT 10
                ''')
            
            results = cursor.fetchall()
        
        if not results:
            return await ctx.send("❌ Aucune donnée trouvée !")
        
        embed = discord.Embed(
            title=f"🏆 Top Utilisateurs - {category.title()}",
            color=0xffd700
        )
        
        top_text = []
        for i, data in enumerate(results, 1):
            user = self.bot.get_user(data[0])
            username = user.name if user else f"Utilisateur {data[0]}"
            
            if category == "balance":
                value = f"{data[1]:,} ArsenalCoins"
            elif category == "level":
                value = f"Niveau {data[1]} ({data[2]:,} XP)"
            else:
                value = f"{data[1]:,} messages"
            
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            top_text.append(f"{medal} **{username}** - {value}")
        
        embed.description = "\n".join(top_text)
        
        await ctx.send(embed=embed)
    
    @users_admin.command(name='info')
    @commands.is_owner()
    async def user_info(self, ctx, user_id: int):
        """ℹ️ Informations détaillées sur un utilisateur"""
        
        user = self.bot.get_user(user_id)
        
        embed = discord.Embed(
            title=f"ℹ️ Info Utilisateur: {user.name if user else user_id}",
            color=0x3498db
        )
        
        # Informations Discord
        if user:
            embed.add_field(
                name="📱 Discord",
                value=f"**Nom:** {user.name}#{user.discriminator}\n**ID:** {user.id}\n**Bot:** {'Oui' if user.bot else 'Non'}",
                inline=True
            )
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        
        # Statistiques bot
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Balance totale
            cursor.execute('SELECT SUM(balance) FROM users WHERE user_id = ?', (user_id,))
            total_balance = cursor.fetchone()[0] or 0
            
            # Serveurs en commun
            cursor.execute('SELECT COUNT(DISTINCT guild_id) FROM users WHERE user_id = ?', (user_id,))
            shared_guilds = cursor.fetchone()[0] or 0
            
            # Messages totaux
            cursor.execute('SELECT SUM(message_count) FROM daily_stats WHERE user_id = ?', (user_id,))
            total_messages = cursor.fetchone()[0] or 0
        
        embed.add_field(
            name="📊 Statistiques Bot",
            value=f"**Balance totale:** {total_balance:,}\n**Serveurs communs:** {shared_guilds}\n**Messages totaux:** {total_messages:,}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @admin.group(name='guilds', invoke_without_command=True)
    @commands.is_owner()
    async def guilds_admin(self, ctx):
        """🏰 Gestion des serveurs"""
        
        embed = discord.Embed(
            title="🏰 Gestion des Serveurs",
            description="Commandes pour gérer les serveurs du bot",
            color=0x3498db
        )
        
        embed.add_field(
            name="Commandes",
            value="`admin guilds list` - Liste des serveurs\n`admin guilds info <id>` - Info serveur\n`admin guilds leave <id>` - Quitter un serveur\n`admin guilds stats` - Statistiques",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @guilds_admin.command(name='list')
    @commands.is_owner()
    async def guilds_list(self, ctx, page: int = 1):
        """📋 Liste des serveurs"""
        
        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)
        
        per_page = 10
        total_pages = (len(guilds) - 1) // per_page + 1
        
        if page < 1 or page > total_pages:
            return await ctx.send(f"❌ Page invalide ! (1-{total_pages})")
        
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        embed = discord.Embed(
            title=f"🏰 Serveurs du Bot ({len(guilds)} total)",
            description=f"Page {page}/{total_pages}",
            color=0x3498db
        )
        
        for guild in guilds[start_index:end_index]:
            embed.add_field(
                name=f"{guild.name}",
                value=f"**ID:** {guild.id}\n**Membres:** {guild.member_count:,}\n**Propriétaire:** {guild.owner}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @guilds_admin.command(name='leave')
    @commands.is_owner()
    async def guild_leave(self, ctx, guild_id: int):
        """🚪 Quitter un serveur"""
        
        guild = self.bot.get_guild(guild_id)
        
        if not guild:
            return await ctx.send("❌ Serveur introuvable !")
        
        confirmation_msg = await ctx.send(f"⚠️ Êtes-vous sûr de vouloir quitter **{guild.name}** ? Réagissez avec ✅ pour confirmer.")
        await confirmation_msg.add_reaction("✅")
        await confirmation_msg.add_reaction("❌")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirmation_msg.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == "❌":
                return await ctx.send("❌ Action annulée.")
            
            await guild.leave()
            await ctx.send(f"✅ J'ai quitté le serveur **{guild.name}**")
            
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps d'attente dépassé. Action annulée.")
    
    @commands.command(name='eval')
    @commands.is_owner()
    async def eval_code(self, ctx, *, code):
        """🐍 Évaluer du code Python"""
        
        # Variables disponibles dans l'environnement d'évaluation
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'discord': discord,
            'commands': commands,
            'asyncio': asyncio,
            'db': self.bot.db
        }
        
        try:
            # Nettoyer le code
            if code.startswith('```python'):
                code = code[9:-3]
            elif code.startswith('```'):
                code = code[3:-3]
            
            # Évaluer le code
            result = eval(code, env)
            
            # Si c'est une coroutine, l'awaiter
            if asyncio.iscoroutine(result):
                result = await result
            
            embed = discord.Embed(
                title="🐍 Évaluation de Code",
                color=0x00ff41
            )
            
            embed.add_field(
                name="📥 Input",
                value=f"```python\n{code[:1000]}\n```",
                inline=False
            )
            
            embed.add_field(
                name="📤 Output",
                value=f"```python\n{str(result)[:1000]}\n```",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur d'Évaluation",
                color=0xff4757
            )
            
            embed.add_field(
                name="📥 Input",
                value=f"```python\n{code[:1000]}\n```",
                inline=False
            )
            
            embed.add_field(
                name="❌ Erreur",
                value=f"```python\n{str(e)[:1000]}\n```",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Tracker l'utilisation des commandes"""
        if not hasattr(self.bot, 'commands_used'):
            self.bot.commands_used = 0
        self.bot.commands_used += 1
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Gérer les erreurs de commandes en mode maintenance"""
        if self.maintenance_mode and not ctx.author.id in self.authorized_users:
            embed = discord.Embed(
                title="🔧 Mode Maintenance",
                description="Le bot est actuellement en maintenance. Veuillez réessayer plus tard.",
                color=0xff4757
            )
            await ctx.send(embed=embed)
            return
        
        # Autres erreurs...
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorer les commandes inconnues
        
        # Logger les erreurs
        print(f"Erreur commande {ctx.command}: {error}")

def setup(bot):
    bot.add_cog(AdminModule(bot))
