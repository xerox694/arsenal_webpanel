"""
📊 Arsenal V4 - Module Statistiques
===================================

Système de statistiques complet pour le serveur
"""

import discord
from discord.ext import commands
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io
import asyncio
from collections import defaultdict, Counter
import calendar

class StatsModule(commands.Cog):
    """Module de statistiques pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        
        # Configuration pour les graphiques
        plt.style.use('dark_background')
        sns.set_palette("viridis")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Tracker les messages pour les statistiques"""
        if message.author.bot or not message.guild:
            return
        
        # Mise à jour des stats en temps réel
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_stats[today]['messages'] += 1
        self.daily_stats[today][f'user_{message.author.id}'] += 1
        
        # Sauvegarder en base de données
        await self.log_message_stats(message)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Tracker les arrivées"""
        await self.log_member_event(member.guild.id, member.id, 'join')
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Tracker les départs"""
        await self.log_member_event(member.guild.id, member.id, 'leave')
    
    @commands.command(name='stats', aliases=['statistiques'])
    async def server_stats(self, ctx):
        """📊 Statistiques du serveur"""
        
        embed = discord.Embed(
            title="📊 Statistiques du Serveur",
            description=f"Données pour {ctx.guild.name}",
            color=0x3498db
        )
        
        # Stats générales
        total_members = ctx.guild.member_count
        bots = sum(1 for m in ctx.guild.members if m.bot)
        humans = total_members - bots
        
        # Stats des rôles
        role_count = len(ctx.guild.roles)
        
        # Stats des canaux
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        
        # Stats de la journée
        today_stats = await self.get_today_stats(ctx.guild.id)
        
        embed.add_field(
            name="👥 Membres",
            value=f"**Total:** {total_members}\n**Humains:** {humans}\n**Bots:** {bots}",
            inline=True
        )
        
        embed.add_field(
            name="📝 Canaux",
            value=f"**Texte:** {text_channels}\n**Vocal:** {voice_channels}\n**Total:** {text_channels + voice_channels}",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Rôles",
            value=f"**Total:** {role_count}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Aujourd'hui",
            value=f"**Messages:** {today_stats['messages']}\n**Arrivées:** {today_stats['joins']}\n**Départs:** {today_stats['leaves']}",
            inline=True
        )
        
        # Date de création du serveur
        created_ago = (datetime.now() - ctx.guild.created_at.replace(tzinfo=None)).days
        embed.add_field(
            name="🎂 Âge du serveur",
            value=f"{created_ago} jours",
            inline=True
        )
        
        # Niveau d'activité
        activity_level = self.get_activity_level(today_stats['messages'], total_members)
        embed.add_field(
            name="⚡ Activité",
            value=activity_level,
            inline=True
        )
        
        embed.timestamp = datetime.now()
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='userstats', aliases=['statsuser'])
    async def user_stats(self, ctx, member: discord.Member = None):
        """👤 Statistiques d'un utilisateur"""
        
        target = member or ctx.author
        
        # Récupérer les stats de l'utilisateur
        user_data = await self.get_user_stats(target.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"👤 Statistiques de {target.display_name}",
            color=target.color if target.color != discord.Color.default() else 0x3498db
        )
        
        # Stats économiques
        balance = self.bot.db.get_user_balance(target.id, ctx.guild.id)
        level_data = self.bot.db.get_user_level(target.id, ctx.guild.id)
        
        embed.add_field(
            name="💰 Économie",
            value=f"**ArsenalCoins:** {balance:,}\n**Niveau:** {level_data['level']}\n**XP:** {level_data['xp']:,}",
            inline=True
        )
        
        # Stats d'activité
        embed.add_field(
            name="📊 Activité",
            value=f"**Messages (7j):** {user_data['messages_7d']:,}\n**Messages (30j):** {user_data['messages_30d']:,}\n**Total:** {user_data['total_messages']:,}",
            inline=True
        )
        
        # Rang de l'utilisateur
        rank = await self.get_user_rank(target.id, ctx.guild.id)
        embed.add_field(
            name="🏆 Classement",
            value=f"**Rang:** #{rank['rank']}/{rank['total']}\n**Top:** {rank['percentage']:.1f}%",
            inline=True
        )
        
        # Date d'arrivée
        joined_ago = (datetime.now() - target.joined_at.replace(tzinfo=None)).days
        embed.add_field(
            name="📅 Membre depuis",
            value=f"{joined_ago} jours",
            inline=True
        )
        
        # Rôle le plus élevé
        highest_role = target.top_role.name if target.top_role.name != "@everyone" else "Aucun"
        embed.add_field(
            name="🎭 Rôle principal",
            value=highest_role,
            inline=True
        )
        
        # Status actuel
        status_emoji = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        
        embed.add_field(
            name="📡 Status",
            value=f"{status_emoji.get(target.status, '❓')} {target.status.name.title()}",
            inline=True
        )
        
        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
    
    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    async def leaderboard(self, ctx, category: str = "level"):
        """🏆 Classements du serveur"""
        
        valid_categories = ["level", "coins", "messages"]
        
        if category.lower() not in valid_categories:
            return await ctx.send(f"❌ Catégorie invalide ! Utilisez: {', '.join(valid_categories)}")
        
        category = category.lower()
        
        # Récupérer le leaderboard
        leaderboard_data = await self.get_leaderboard(ctx.guild.id, category)
        
        if not leaderboard_data:
            return await ctx.send("❌ Aucune donnée disponible !")
        
        # Créer l'embed
        category_names = {
            "level": "🏆 Classement par Niveau",
            "coins": "💰 Classement par ArsenalCoins",
            "messages": "📝 Classement par Messages"
        }
        
        embed = discord.Embed(
            title=category_names[category],
            description=f"Top {min(len(leaderboard_data), 10)} sur {ctx.guild.name}",
            color=0xf1c40f
        )
        
        # Emojis pour le podium
        medals = ["🥇", "🥈", "🥉"]
        
        leaderboard_text = []
        
        for i, data in enumerate(leaderboard_data[:10]):
            user = ctx.guild.get_member(data['user_id'])
            if not user:
                continue
            
            # Emoji pour la position
            position_emoji = medals[i] if i < 3 else f"{i+1}."
            
            # Formatage selon la catégorie
            if category == "level":
                value_text = f"Niveau {data['level']} ({data['xp']:,} XP)"
            elif category == "coins":
                value_text = f"{data['balance']:,} ArsenalCoins"
            else:  # messages
                value_text = f"{data['message_count']:,} messages"
            
            leaderboard_text.append(f"{position_emoji} **{user.display_name}** - {value_text}")
        
        embed.description += "\n\n" + "\n".join(leaderboard_text)
        
        # Position de l'utilisateur actuel
        user_rank = next((i+1 for i, data in enumerate(leaderboard_data) 
                         if data['user_id'] == ctx.author.id), None)
        
        if user_rank:
            embed.set_footer(text=f"Votre position: #{user_rank}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='activity', aliases=['activité'])
    async def activity_graph(self, ctx, period: str = "7d"):
        """📈 Graphique d'activité du serveur"""
        
        # Valider la période
        valid_periods = {"1d": 1, "7d": 7, "30d": 30}
        
        if period not in valid_periods:
            return await ctx.send(f"❌ Période invalide ! Utilisez: {', '.join(valid_periods.keys())}")
        
        days = valid_periods[period]
        
        # Récupérer les données
        activity_data = await self.get_activity_data(ctx.guild.id, days)
        
        if not activity_data:
            return await ctx.send("❌ Pas assez de données pour générer le graphique !")
        
        # Créer le graphique
        plt.figure(figsize=(12, 6))
        
        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in activity_data]
        messages = [d['message_count'] for d in activity_data]
        
        plt.plot(dates, messages, marker='o', linewidth=2, markersize=6)
        plt.title(f'Activité du serveur - {period}', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Nombre de messages', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Formatage des dates sur l'axe X
        if days <= 7:
            plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
        else:
            plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Sauvegarder en buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        # Envoyer le graphique
        file = discord.File(buffer, filename='activity.png')
        
        embed = discord.Embed(
            title="📈 Graphique d'activité",
            description=f"Activité du serveur sur les {days} derniers jours",
            color=0x3498db
        )
        
        embed.set_image(url="attachment://activity.png")
        
        # Stats supplémentaires
        total_messages = sum(messages)
        avg_messages = total_messages / len(messages) if messages else 0
        
        embed.add_field(
            name="📊 Résumé",
            value=f"**Total:** {total_messages:,} messages\n**Moyenne:** {avg_messages:.1f} messages/jour",
            inline=False
        )
        
        await ctx.send(embed=embed, file=file)
        buffer.close()
    
    @commands.command(name='channels', aliases=['chanstats'])
    @commands.has_permissions(manage_guild=True)
    async def channel_stats(self, ctx, days: int = 7):
        """📝 Statistiques par canal"""
        
        if days > 30:
            return await ctx.send("❌ Maximum 30 jours !")
        
        channel_data = await self.get_channel_stats(ctx.guild.id, days)
        
        if not channel_data:
            return await ctx.send("❌ Aucune donnée disponible !")
        
        embed = discord.Embed(
            title=f"📝 Statistiques des canaux ({days}j)",
            description=f"Activité sur {ctx.guild.name}",
            color=0x3498db
        )
        
        # Top 10 des canaux les plus actifs
        stats_text = []
        for i, data in enumerate(channel_data[:10], 1):
            channel = ctx.guild.get_channel(data['channel_id'])
            if channel:
                stats_text.append(f"{i}. **#{channel.name}** - {data['message_count']:,} messages")
        
        embed.add_field(
            name="🏆 Canaux les plus actifs",
            value="\n".join(stats_text) if stats_text else "Aucune donnée",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def log_message_stats(self, message):
        """Logger les statistiques de message"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO daily_stats 
                (guild_id, user_id, channel_id, date, message_count)
                VALUES (?, ?, ?, DATE('now'), 0)
            ''', (message.guild.id, message.author.id, message.channel.id))
            
            cursor.execute('''
                UPDATE daily_stats 
                SET message_count = message_count + 1
                WHERE guild_id = ? AND user_id = ? AND channel_id = ? AND date = DATE('now')
            ''', (message.guild.id, message.author.id, message.channel.id))
            
            conn.commit()
    
    async def log_member_event(self, guild_id: int, user_id: int, event_type: str):
        """Logger les événements de membres"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO member_events (guild_id, user_id, event_type)
                VALUES (?, ?, ?)
            ''', (guild_id, user_id, event_type))
            conn.commit()
    
    async def get_today_stats(self, guild_id: int) -> dict:
        """Récupérer les stats du jour"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Messages du jour
            cursor.execute('''
                SELECT COALESCE(SUM(message_count), 0)
                FROM daily_stats
                WHERE guild_id = ? AND date = DATE('now')
            ''', (guild_id,))
            messages = cursor.fetchone()[0]
            
            # Arrivées du jour
            cursor.execute('''
                SELECT COUNT(*)
                FROM member_events
                WHERE guild_id = ? AND event_type = 'join' AND DATE(timestamp) = DATE('now')
            ''', (guild_id,))
            joins = cursor.fetchone()[0]
            
            # Départs du jour
            cursor.execute('''
                SELECT COUNT(*)
                FROM member_events
                WHERE guild_id = ? AND event_type = 'leave' AND DATE(timestamp) = DATE('now')
            ''', (guild_id,))
            leaves = cursor.fetchone()[0]
            
            return {
                'messages': messages,
                'joins': joins,
                'leaves': leaves
            }
    
    def get_activity_level(self, messages: int, members: int) -> str:
        """Déterminer le niveau d'activité"""
        if members == 0:
            return "❓ Inconnu"
        
        ratio = messages / members
        
        if ratio >= 10:
            return "🔥 Très active"
        elif ratio >= 5:
            return "⚡ Active"
        elif ratio >= 2:
            return "📈 Modérée"
        elif ratio >= 0.5:
            return "📉 Faible"
        else:
            return "💤 Très faible"
    
    async def get_user_stats(self, user_id: int, guild_id: int) -> dict:
        """Récupérer les stats d'un utilisateur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Messages des 7 derniers jours
            cursor.execute('''
                SELECT COALESCE(SUM(message_count), 0)
                FROM daily_stats
                WHERE guild_id = ? AND user_id = ? AND date >= DATE('now', '-7 days')
            ''', (guild_id, user_id))
            messages_7d = cursor.fetchone()[0]
            
            # Messages des 30 derniers jours
            cursor.execute('''
                SELECT COALESCE(SUM(message_count), 0)
                FROM daily_stats
                WHERE guild_id = ? AND user_id = ? AND date >= DATE('now', '-30 days')
            ''', (guild_id, user_id))
            messages_30d = cursor.fetchone()[0]
            
            # Total des messages
            cursor.execute('''
                SELECT COALESCE(SUM(message_count), 0)
                FROM daily_stats
                WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            total_messages = cursor.fetchone()[0]
            
            return {
                'messages_7d': messages_7d,
                'messages_30d': messages_30d,
                'total_messages': total_messages
            }
    
    async def get_user_rank(self, user_id: int, guild_id: int) -> dict:
        """Récupérer le rang d'un utilisateur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Classement par XP
            cursor.execute('''
                SELECT user_id, ROW_NUMBER() OVER (ORDER BY xp DESC) as rank
                FROM users
                WHERE guild_id = ?
                ORDER BY xp DESC
            ''', (guild_id,))
            
            rankings = cursor.fetchall()
            total_users = len(rankings)
            
            user_rank = next((rank for uid, rank in rankings if uid == user_id), total_users)
            percentage = ((total_users - user_rank + 1) / total_users * 100) if total_users > 0 else 0
            
            return {
                'rank': user_rank,
                'total': total_users,
                'percentage': percentage
            }
    
    async def get_leaderboard(self, guild_id: int, category: str) -> list:
        """Récupérer le classement"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            if category == "level":
                cursor.execute('''
                    SELECT user_id, level, xp
                    FROM users
                    WHERE guild_id = ?
                    ORDER BY level DESC, xp DESC
                    LIMIT 20
                ''', (guild_id,))
                
                return [{'user_id': row[0], 'level': row[1], 'xp': row[2]} for row in cursor.fetchall()]
                
            elif category == "coins":
                cursor.execute('''
                    SELECT user_id, balance
                    FROM users
                    WHERE guild_id = ?
                    ORDER BY balance DESC
                    LIMIT 20
                ''', (guild_id,))
                
                return [{'user_id': row[0], 'balance': row[1]} for row in cursor.fetchall()]
                
            else:  # messages
                cursor.execute('''
                    SELECT user_id, SUM(message_count) as total
                    FROM daily_stats
                    WHERE guild_id = ?
                    GROUP BY user_id
                    ORDER BY total DESC
                    LIMIT 20
                ''', (guild_id,))
                
                return [{'user_id': row[0], 'message_count': row[1]} for row in cursor.fetchall()]
    
    async def get_activity_data(self, guild_id: int, days: int) -> list:
        """Récupérer les données d'activité"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, SUM(message_count) as total
                FROM daily_stats
                WHERE guild_id = ? AND date >= DATE('now', '-{} days')
                GROUP BY date
                ORDER BY date
            '''.format(days), (guild_id,))
            
            return [{'date': row[0], 'message_count': row[1]} for row in cursor.fetchall()]
    
    async def get_channel_stats(self, guild_id: int, days: int) -> list:
        """Récupérer les stats par canal"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT channel_id, SUM(message_count) as total
                FROM daily_stats
                WHERE guild_id = ? AND date >= DATE('now', '-{} days')
                GROUP BY channel_id
                ORDER BY total DESC
            '''.format(days), (guild_id,))
            
            return [{'channel_id': row[0], 'message_count': row[1]} for row in cursor.fetchall()]

def setup(bot):
    bot.add_cog(StatsModule(bot))
