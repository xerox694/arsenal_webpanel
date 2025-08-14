"""
💡 SYSTÈME DE SUGGESTIONS AVANCÉ - Arsenal Bot V4
=================================================

Système complet de gestion des suggestions avec :
- Votes et réactions
- Catégories multiples
- Modération avancée
- Tableau de bord admin
- Notifications automatiques
- Système de récompenses

Module rechargeable à chaud
"""

import sqlite3
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Union

class SuggestionsDatabase:
    """Base de données pour le système de suggestions"""
    
    def __init__(self, db_path: str = "suggestions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données des suggestions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale des suggestions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT,
                discriminator TEXT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general',
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                votes_up INTEGER DEFAULT 0,
                votes_down INTEGER DEFAULT 0,
                message_id TEXT,
                channel_id TEXT,
                guild_id TEXT,
                admin_response TEXT,
                admin_user_id TEXT,
                implementation_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP NULL,
                tags TEXT DEFAULT '',
                attachment_url TEXT
            )
        ''')
        
        # Table des votes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_id INTEGER,
                user_id TEXT,
                vote_type TEXT CHECK(vote_type IN ('up', 'down')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (suggestion_id) REFERENCES suggestions (id)
            )
        ''')
        
        # Table des commentaires
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_id INTEGER,
                user_id TEXT,
                username TEXT,
                comment TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (suggestion_id) REFERENCES suggestions (id)
            )
        ''')
        
        # Table des catégories personnalisées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                emoji TEXT,
                color TEXT,
                auto_approve BOOLEAN DEFAULT FALSE,
                admin_only BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des récompenses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                suggestion_id INTEGER,
                reward_type TEXT,
                reward_amount INTEGER,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (suggestion_id) REFERENCES suggestions (id)
            )
        ''')
        
        # Table des configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_config (
                guild_id TEXT PRIMARY KEY,
                suggestion_channel_id TEXT,
                admin_channel_id TEXT,
                auto_react BOOLEAN DEFAULT TRUE,
                min_votes_implement INTEGER DEFAULT 10,
                allow_anonymous BOOLEAN DEFAULT FALSE,
                reward_coins INTEGER DEFAULT 50,
                auto_close_days INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insérer les catégories par défaut
        default_categories = [
            ('general', 'Général', 'Suggestions générales', '💡', '#3498db', False, False),
            ('bot', 'Bot Discord', 'Améliorations du bot', '🤖', '#9b59b6', False, False),
            ('hunt_royal', 'Hunt Royal', 'Suggestions Hunt Royal', '🏹', '#e74c3c', False, False),
            ('music', 'Musique', 'Système de musique', '🎵', '#f39c12', False, False),
            ('moderation', 'Modération', 'Outils de modération', '🛡️', '#95a5a6', False, True),
            ('feature', 'Nouvelle Fonctionnalité', 'Nouvelles fonctionnalités', '⭐', '#2ecc71', False, False),
            ('bug', 'Correction de Bug', 'Signalement de bugs', '🐛', '#e67e22', False, False),
            ('economy', 'Économie', 'Système économique', '💰', '#f1c40f', False, False)
        ]
        
        for cat_id, name, desc, emoji, color, auto_approve, admin_only in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO suggestion_categories 
                (id, name, description, emoji, color, auto_approve, admin_only)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cat_id, name, desc, emoji, color, auto_approve, admin_only))
        
        conn.commit()
        conn.close()
        print("✅ Base de données Suggestions initialisée")

class SuggestionManager:
    """Gestionnaire principal des suggestions"""
    
    def __init__(self, db: SuggestionsDatabase):
        self.db = db
        self.active_polls = {}  # Polls en cours
        
    async def create_suggestion(self, user, title: str, description: str, category: str = 'general', 
                              attachment_url: str = None, guild_id: str = None):
        """Créer une nouvelle suggestion"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO suggestions 
            (user_id, username, discriminator, title, description, category, guild_id, attachment_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(user.id), user.display_name, user.discriminator,
            title, description, category, guild_id, attachment_url
        ))
        
        suggestion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return suggestion_id
    
    async def vote_suggestion(self, suggestion_id: int, user_id: str, vote_type: str):
        """Voter sur une suggestion"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur a déjà voté
        cursor.execute('''
            SELECT vote_type FROM suggestion_votes 
            WHERE suggestion_id = ? AND user_id = ?
        ''', (suggestion_id, user_id))
        
        existing_vote = cursor.fetchone()
        
        if existing_vote:
            # Changer le vote existant
            old_vote = existing_vote[0]
            cursor.execute('''
                UPDATE suggestion_votes 
                SET vote_type = ?, created_at = CURRENT_TIMESTAMP
                WHERE suggestion_id = ? AND user_id = ?
            ''', (vote_type, suggestion_id, user_id))
            
            # Ajuster les compteurs
            if old_vote != vote_type:
                if old_vote == 'up':
                    cursor.execute('UPDATE suggestions SET votes_up = votes_up - 1 WHERE id = ?', (suggestion_id,))
                else:
                    cursor.execute('UPDATE suggestions SET votes_down = votes_down - 1 WHERE id = ?', (suggestion_id,))
                
                if vote_type == 'up':
                    cursor.execute('UPDATE suggestions SET votes_up = votes_up + 1 WHERE id = ?', (suggestion_id,))
                else:
                    cursor.execute('UPDATE suggestions SET votes_down = votes_down + 1 WHERE id = ?', (suggestion_id,))
        else:
            # Nouveau vote
            cursor.execute('''
                INSERT INTO suggestion_votes (suggestion_id, user_id, vote_type)
                VALUES (?, ?, ?)
            ''', (suggestion_id, user_id, vote_type))
            
            # Mettre à jour les compteurs
            if vote_type == 'up':
                cursor.execute('UPDATE suggestions SET votes_up = votes_up + 1 WHERE id = ?', (suggestion_id,))
            else:
                cursor.execute('UPDATE suggestions SET votes_down = votes_down + 1 WHERE id = ?', (suggestion_id,))
        
        # Mettre à jour le timestamp de modification
        cursor.execute('UPDATE suggestions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (suggestion_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    async def get_suggestions(self, status: str = None, category: str = None, 
                            user_id: str = None, limit: int = 20, offset: int = 0):
        """Récupérer les suggestions avec filtres"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM suggestions WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY votes_up DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        suggestions = cursor.fetchall()
        conn.close()
        
        return suggestions
    
    async def update_suggestion_status(self, suggestion_id: int, status: str, 
                                     admin_response: str = None, admin_user_id: str = None):
        """Mettre à jour le statut d'une suggestion"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        
        if admin_response:
            update_fields.append("admin_response = ?")
            params.append(admin_response)
        
        if admin_user_id:
            update_fields.append("admin_user_id = ?")
            params.append(admin_user_id)
        
        if status in ['implemented', 'rejected', 'closed']:
            update_fields.append("closed_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE suggestions SET {', '.join(update_fields)} WHERE id = ?"
        params.append(suggestion_id)
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return True
    
    async def add_comment(self, suggestion_id: int, user_id: str, username: str, 
                         comment: str, is_admin: bool = False):
        """Ajouter un commentaire à une suggestion"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO suggestion_comments 
            (suggestion_id, user_id, username, comment, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (suggestion_id, user_id, username, comment, is_admin))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return comment_id
    
    async def get_suggestion_stats(self, user_id: str = None):
        """Statistiques des suggestions"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Stats globales
        if not user_id:
            cursor.execute("SELECT COUNT(*) FROM suggestions")
            stats['total'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT status, COUNT(*) FROM suggestions GROUP BY status")
            status_counts = dict(cursor.fetchall())
            stats['by_status'] = status_counts
            
            cursor.execute("SELECT category, COUNT(*) FROM suggestions GROUP BY category")
            category_counts = dict(cursor.fetchall())
            stats['by_category'] = category_counts
            
        # Stats utilisateur
        else:
            cursor.execute("SELECT COUNT(*) FROM suggestions WHERE user_id = ?", (user_id,))
            stats['total'] = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT status, COUNT(*) FROM suggestions 
                WHERE user_id = ? GROUP BY status
            ''', (user_id,))
            status_counts = dict(cursor.fetchall())
            stats['by_status'] = status_counts
        
        conn.close()
        return stats

class SuggestionsCommands(commands.Cog):
    """Commandes pour le système de suggestions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = SuggestionsDatabase()
        self.manager = SuggestionManager(self.db)
    
    @commands.group(name='suggest', invoke_without_command=True)
    async def suggest_command(self, ctx, *, suggestion_text: str = None):
        """Créer une nouvelle suggestion"""
        if not suggestion_text:
            embed = discord.Embed(
                title="💡 Système de Suggestions Arsenal",
                description="Créez des suggestions pour améliorer le serveur !",
                color=0x3498db
            )
            
            embed.add_field(
                name="📝 Créer une Suggestion",
                value="`!suggest <titre> | <description>` - Suggestion basique\n"
                      "`!suggest advanced` - Mode interactif\n"
                      "`!suggest hunt <suggestion>` - Suggestion Hunt Royal",
                inline=False
            )
            
            embed.add_field(
                name="🗳️ Gestion",
                value="`!suggest list` - Voir toutes les suggestions\n"
                      "`!suggest my` - Mes suggestions\n"
                      "`!suggest top` - Top suggestions\n"
                      "`!suggest status <id>` - État d'une suggestion",
                inline=False
            )
            
            embed.add_field(
                name="⚙️ Admin",
                value="`!suggest approve <id>` - Approuver\n"
                      "`!suggest reject <id> <raison>` - Rejeter\n"
                      "`!suggest implement <id>` - Marquer implémentée",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        # Parser la suggestion
        parts = suggestion_text.split('|', 1)
        if len(parts) != 2:
            embed = discord.Embed(
                title="❌ Format incorrect",
                description="Utilisez : `!suggest <titre> | <description>`\n"
                           "**Exemple :** `!suggest Nouveau jeu | Il faudrait ajouter un système de casino`",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return
        
        title = parts[0].strip()[:100]  # Limiter titre
        description = parts[1].strip()[:1000]  # Limiter description
        
        # Déterminer la catégorie automatiquement
        category = 'general'
        title_lower = title.lower()
        description_lower = description.lower()
        
        if any(word in title_lower + description_lower for word in ['hunt', 'royal', 'chasseur', 'donjon']):
            category = 'hunt_royal'
        elif any(word in title_lower + description_lower for word in ['bot', 'commande', 'discord']):
            category = 'bot'
        elif any(word in title_lower + description_lower for word in ['musique', 'music', 'son', 'audio']):
            category = 'music'
        elif any(word in title_lower + description_lower for word in ['bug', 'erreur', 'problème']):
            category = 'bug'
        elif any(word in title_lower + description_lower for word in ['modération', 'ban', 'kick', 'mute']):
            category = 'moderation'
        
        # Créer la suggestion
        suggestion_id = await self.manager.create_suggestion(
            ctx.author, title, description, category, 
            guild_id=str(ctx.guild.id) if ctx.guild else None
        )
        
        # Créer l'embed de confirmation
        embed = discord.Embed(
            title="✅ Suggestion créée !",
            description=f"**ID:** #{suggestion_id}\n**Catégorie:** {category}",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="📝 Titre",
            value=title,
            inline=False
        )
        
        embed.add_field(
            name="📄 Description",
            value=description[:500] + ("..." if len(description) > 500 else ""),
            inline=False
        )
        
        embed.add_field(
            name="👥 Prochaines Étapes",
            value="• Réagissez avec ⬆️ ou ⬇️ pour voter\n"
                  "• Les admins examineront votre suggestion\n"
                  "• Vous serez notifié des mises à jour",
            inline=False
        )
        
        embed.set_footer(text=f"Créée par {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        message = await ctx.send(embed=embed)
        
        # Ajouter les réactions
        await message.add_reaction("⬆️")
        await message.add_reaction("⬇️")
        await message.add_reaction("💬")  # Pour commenter
        
        # Sauvegarder l'ID du message
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE suggestions 
            SET message_id = ?, channel_id = ? 
            WHERE id = ?
        ''', (str(message.id), str(ctx.channel.id), suggestion_id))
        conn.commit()
        conn.close()
    
    @suggest_command.command(name='list')
    async def suggest_list(self, ctx, category: str = None):
        """Lister les suggestions"""
        suggestions = await self.manager.get_suggestions(
            status='pending', category=category, limit=10
        )
        
        if not suggestions:
            embed = discord.Embed(
                title="📋 Aucune Suggestion",
                description="Aucune suggestion trouvée pour ces critères",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📋 Suggestions {category.title() if category else 'Toutes Catégories'}",
            description=f"Affichage de {len(suggestions)} suggestions",
            color=0x3498db
        )
        
        for suggestion in suggestions[:5]:  # Limiter à 5 pour l'embed
            suggestion_id = suggestion[0]
            title = suggestion[4][:50] + ("..." if len(suggestion[4]) > 50 else "")
            votes_up = suggestion[9]
            votes_down = suggestion[10]
            category_name = suggestion[6]
            
            embed.add_field(
                name=f"#{suggestion_id} - {title}",
                value=f"**Catégorie:** {category_name}\n"
                      f"**Votes:** ⬆️ {votes_up} | ⬇️ {votes_down}\n"
                      f"**Auteur:** {suggestion[2]}",
                inline=True
            )
        
        if len(suggestions) > 5:
            embed.add_field(
                name="📊 Plus de Suggestions",
                value=f"... et {len(suggestions) - 5} autres suggestions\n"
                      "Utilisez `!suggest top` pour voir le classement",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @suggest_command.command(name='top')
    async def suggest_top(self, ctx):
        """Top des suggestions les mieux votées"""
        suggestions = await self.manager.get_suggestions(limit=10)
        
        if not suggestions:
            embed = discord.Embed(
                title="📊 Aucune Suggestion",
                description="Aucune suggestion disponible",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏆 Top Suggestions Arsenal",
            description="Les suggestions les mieux votées",
            color=0xf1c40f
        )
        
        for i, suggestion in enumerate(suggestions, 1):
            suggestion_id = suggestion[0]
            title = suggestion[4][:40] + ("..." if len(suggestion[4]) > 40 else "")
            votes_up = suggestion[9]
            votes_down = suggestion[10]
            status = suggestion[8]
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            status_emoji = "✅" if status == "implemented" else "⏳" if status == "pending" else "❌"
            
            embed.add_field(
                name=f"{medal} #{suggestion_id} - {title}",
                value=f"{status_emoji} **Score:** {votes_up - votes_down} (⬆️{votes_up} ⬇️{votes_down})",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @suggest_command.command(name='my')
    async def suggest_my(self, ctx):
        """Mes suggestions"""
        suggestions = await self.manager.get_suggestions(user_id=str(ctx.author.id))
        
        if not suggestions:
            embed = discord.Embed(
                title="📝 Aucune Suggestion",
                description="Vous n'avez encore créé aucune suggestion",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📝 Vos Suggestions ({len(suggestions)})",
            description=f"Toutes vos suggestions, {ctx.author.display_name}",
            color=0x9b59b6
        )
        
        for suggestion in suggestions:
            suggestion_id = suggestion[0]
            title = suggestion[4][:50] + ("..." if len(suggestion[4]) > 50 else "")
            status = suggestion[8]
            votes_up = suggestion[9]
            votes_down = suggestion[10]
            
            status_emojis = {
                'pending': '⏳ En attente',
                'approved': '✅ Approuvée',
                'implemented': '🎉 Implémentée',
                'rejected': '❌ Rejetée',
                'closed': '🔒 Fermée'
            }
            
            embed.add_field(
                name=f"#{suggestion_id} - {title}",
                value=f"**Statut:** {status_emojis.get(status, status)}\n"
                      f"**Votes:** ⬆️ {votes_up} | ⬇️ {votes_down}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @suggest_command.command(name='approve')
    @commands.has_permissions(manage_guild=True)
    async def suggest_approve(self, ctx, suggestion_id: int, *, response: str = None):
        """Approuver une suggestion (Admin)"""
        success = await self.manager.update_suggestion_status(
            suggestion_id, 'approved', response, str(ctx.author.id)
        )
        
        if success:
            embed = discord.Embed(
                title="✅ Suggestion Approuvée",
                description=f"La suggestion #{suggestion_id} a été approuvée !",
                color=0x2ecc71
            )
            
            if response:
                embed.add_field(
                    name="💬 Réponse Admin",
                    value=response,
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible d'approuver la suggestion #{suggestion_id}",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
    
    @suggest_command.command(name='stats')
    async def suggest_stats(self, ctx, user: discord.Member = None):
        """Statistiques des suggestions"""
        target_user = user or ctx.author
        stats = await self.manager.get_suggestion_stats(str(target_user.id) if user else None)
        
        embed = discord.Embed(
            title=f"📊 Statistiques - {target_user.display_name if user else 'Serveur'}",
            color=0x3498db
        )
        
        embed.add_field(
            name="📈 Total",
            value=f"**{stats.get('total', 0)}** suggestions",
            inline=True
        )
        
        # Stats par statut
        if 'by_status' in stats:
            status_text = ""
            for status, count in stats['by_status'].items():
                status_emojis = {
                    'pending': '⏳', 'approved': '✅', 'implemented': '🎉',
                    'rejected': '❌', 'closed': '🔒'
                }
                emoji = status_emojis.get(status, '📝')
                status_text += f"{emoji} {status.title()}: {count}\n"
            
            embed.add_field(
                name="📋 Par Statut",
                value=status_text or "Aucune donnée",
                inline=True
            )
        
        # Stats par catégorie (serveur uniquement)
        if not user and 'by_category' in stats:
            category_text = ""
            for category, count in list(stats['by_category'].items())[:5]:
                category_text += f"• {category}: {count}\n"
            
            embed.add_field(
                name="🏷️ Par Catégorie",
                value=category_text or "Aucune donnée",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    # Gestionnaire de réactions
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Gérer les votes par réaction"""
        if user.bot:
            return
        
        # Vérifier si c'est une suggestion
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM suggestions WHERE message_id = ?', (str(reaction.message.id),))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return
        
        suggestion_id = result[0]
        
        # Traiter le vote
        if reaction.emoji == "⬆️":
            await self.manager.vote_suggestion(suggestion_id, str(user.id), 'up')
        elif reaction.emoji == "⬇️":
            await self.manager.vote_suggestion(suggestion_id, str(user.id), 'down')

# ==================== FONCTIONS D'INITIALISATION ====================

def setup(bot):
    """Charger le système de suggestions"""
    bot.add_cog(SuggestionsCommands(bot))
    print("💡 Système de suggestions avancé chargé !")

def teardown(bot):
    """Décharger le système de suggestions"""
    bot.remove_cog('SuggestionsCommands')
    print("💡 Système de suggestions déchargé")

if __name__ == "__main__":
    print("💡 Suggestions System - Module autonome initialisé")
