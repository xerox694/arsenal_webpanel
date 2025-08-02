#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎫 ARSENAL V4 - SYSTÈME DE TICKETS ULTRA-AVANCÉ
Système de tickets avec catégories, rôles, auto-réponses, statistiques
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.logger import log

class TicketSystem:
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/ticket_config.json"
        self.tickets_path = "data/tickets_data.json"
        self.load_config()
        self.load_tickets_data()
        
    def load_config(self):
        """Charge la configuration des tickets"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                log.info("🎫 Configuration tickets chargée")
            except Exception as e:
                log.error(f"❌ Erreur chargement ticket config: {e}")
                self.config = {"servers": {}}
        else:
            self.config = {"servers": {}}
            self.save_config()
    
    def load_tickets_data(self):
        """Charge les données des tickets"""
        if os.path.exists(self.tickets_path):
            try:
                with open(self.tickets_path, "r", encoding="utf-8") as f:
                    self.tickets_data = json.load(f)
                log.info("🎫 Données tickets chargées")
            except Exception as e:
                log.error(f"❌ Erreur chargement tickets data: {e}")
                self.tickets_data = {"servers": {}}
        else:
            self.tickets_data = {"servers": {}}
            self.save_tickets_data()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            log.info("💾 Configuration tickets sauvegardée")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde ticket config: {e}")
    
    def save_tickets_data(self):
        """Sauvegarde les données des tickets"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.tickets_path, "w", encoding="utf-8") as f:
                json.dump(self.tickets_data, f, indent=4, ensure_ascii=False)
            log.info("💾 Données tickets sauvegardées")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde tickets data: {e}")
    
    def get_server_config(self, guild_id: int) -> dict:
        """Récupère la config tickets d'un serveur"""
        guild_id = str(guild_id)
        if guild_id not in self.config["servers"]:
            self.config["servers"][guild_id] = self.get_default_config()
            self.save_config()
        return self.config["servers"][guild_id]
    
    def get_default_config(self) -> dict:
        """Configuration par défaut"""
        return {
            "enabled": True,
            "category_id": None,  # Catégorie pour les tickets
            "support_roles": [],  # Rôles qui peuvent voir tous les tickets
            "log_channel": None,  # Salon de logs
            "max_tickets_per_user": 3,  # Tickets max par utilisateur
            "auto_close_hours": 72,  # Auto-fermeture après X heures d'inactivité
            "ticket_categories": {
                "support": {
                    "name": "🆘 Support Général",
                    "description": "Besoin d'aide générale",
                    "auto_response": "Merci pour votre demande de support ! Un membre de l'équipe vous répondra bientôt.",
                    "roles": [],  # Rôles notifiés
                    "emoji": "🆘"
                },
                "bug": {
                    "name": "🐛 Signaler un Bug",
                    "description": "Signaler un problème technique",
                    "auto_response": "Merci de signaler ce bug ! Veuillez décrire le problème en détail.",
                    "roles": [],
                    "emoji": "🐛"
                },
                "suggestion": {
                    "name": "💡 Suggestion",
                    "description": "Proposer une amélioration",
                    "auto_response": "Merci pour votre suggestion ! Nous allons l'étudier attentivement.",
                    "roles": [],
                    "emoji": "💡"
                },
                "report": {
                    "name": "⚠️ Signalement",
                    "description": "Signaler un utilisateur",
                    "auto_response": "Merci pour votre signalement. Veuillez fournir des preuves si possible.",
                    "roles": [],
                    "emoji": "⚠️"
                }
            }
        }
    
    def get_server_tickets(self, guild_id: int) -> dict:
        """Récupère les tickets d'un serveur"""
        guild_id = str(guild_id)
        if guild_id not in self.tickets_data["servers"]:
            self.tickets_data["servers"][guild_id] = {"tickets": {}, "stats": {"total": 0, "closed": 0, "open": 0}}
            self.save_tickets_data()
        return self.tickets_data["servers"][guild_id]
    
    async def create_ticket(self, interaction: discord.Interaction, category: str, user: discord.Member) -> Optional[discord.TextChannel]:
        """Crée un nouveau ticket"""
        config = self.get_server_config(interaction.guild.id)
        tickets_data = self.get_server_tickets(interaction.guild.id)
        
        if not config["enabled"]:
            return None
        
        # Vérifier la limite de tickets par utilisateur
        user_tickets = [t for t in tickets_data["tickets"].values() if t["user_id"] == user.id and t["status"] == "open"]
        if len(user_tickets) >= config["max_tickets_per_user"]:
            return None
        
        # Récupérer la catégorie Discord
        category_channel = interaction.guild.get_channel(config["category_id"])
        if not category_channel:
            return None
        
        # Générer un ID unique pour le ticket
        ticket_id = len(tickets_data["tickets"]) + 1
        ticket_name = f"ticket-{user.display_name}-{ticket_id}".lower().replace(" ", "-")
        
        # Permissions du ticket
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_messages=True
            )
        }
        
        # Ajouter les rôles de support
        for role_id in config["support_roles"]:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True
                )
        
        # Ajouter les rôles spécifiques à la catégorie
        category_config = config["ticket_categories"].get(category, {})
        for role_id in category_config.get("roles", []):
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )
        
        try:
            # Créer le salon
            ticket_channel = await category_channel.create_text_channel(
                name=ticket_name,
                overwrites=overwrites,
                topic=f"Ticket de {user.display_name} | Catégorie: {category} | ID: {ticket_id}"
            )
            
            # Créer l'embed de bienvenue
            category_info = config["ticket_categories"].get(category, {})
            embed = discord.Embed(
                title=f"🎫 Ticket #{ticket_id}",
                description=f"**Créé par:** {user.mention}\n**Catégorie:** {category_info.get('name', category)}\n**Date:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                color=discord.Color.blue()
            )
            
            if category_info.get("auto_response"):
                embed.add_field(
                    name="📝 Message automatique",
                    value=category_info["auto_response"],
                    inline=False
                )
            
            embed.add_field(
                name="🔧 Actions disponibles",
                value="• Utilisez `/ticket close` pour fermer le ticket\n• Utilisez `/ticket add @user` pour ajouter quelqu'un\n• Utilisez `/ticket remove @user` pour retirer quelqu'un",
                inline=False
            )
            
            embed.set_footer(text="Arsenal Ticket System • Répondez dans ce salon")
            
            # Créer les boutons de contrôle
            view = TicketControlView(self, ticket_id, user.id)
            
            # Envoyer le message de bienvenue
            await ticket_channel.send(f"{user.mention}", embed=embed, view=view)
            
            # Notifier les rôles
            mentions = []
            for role_id in config["support_roles"] + category_info.get("roles", []):
                role = interaction.guild.get_role(role_id)
                if role:
                    mentions.append(role.mention)
            
            if mentions:
                await ticket_channel.send(f"👋 {' '.join(mentions)}, nouveau ticket !")
            
            # Enregistrer le ticket
            ticket_data = {
                "id": ticket_id,
                "user_id": user.id,
                "channel_id": ticket_channel.id,
                "category": category,
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "messages_count": 0
            }
            
            tickets_data["tickets"][str(ticket_id)] = ticket_data
            tickets_data["stats"]["total"] += 1
            tickets_data["stats"]["open"] += 1
            self.save_tickets_data()
            
            # Log l'action
            await self.log_action(interaction.guild, "Ticket créé", user, f"Ticket #{ticket_id} - {category}")
            
            log.info(f"🎫 Ticket #{ticket_id} créé par {user.display_name} ({category})")
            return ticket_channel
            
        except Exception as e:
            log.error(f"❌ Erreur création ticket: {e}")
            return None
    
    async def close_ticket(self, interaction: discord.Interaction, ticket_id: int, closer: discord.Member, reason: str = "Fermé par l'utilisateur"):
        """Ferme un ticket"""
        tickets_data = self.get_server_tickets(interaction.guild.id)
        ticket_data = tickets_data["tickets"].get(str(ticket_id))
        
        if not ticket_data or ticket_data["status"] != "open":
            return False
        
        channel = interaction.guild.get_channel(ticket_data["channel_id"])
        if not channel:
            return False
        
        # Créer un transcript du ticket
        transcript = await self.create_transcript(channel)
        
        # Envoyer le transcript au créateur du ticket
        user = interaction.guild.get_member(ticket_data["user_id"])
        if user:
            try:
                embed = discord.Embed(
                    title=f"🎫 Ticket #{ticket_id} fermé",
                    description=f"**Raison:** {reason}\n**Fermé par:** {closer.mention}",
                    color=discord.Color.red()
                )
                await user.send(embed=embed, file=transcript)
            except:
                pass
        
        # Marquer comme fermé
        ticket_data["status"] = "closed"
        ticket_data["closed_at"] = datetime.now().isoformat()
        ticket_data["closed_by"] = closer.id
        ticket_data["close_reason"] = reason
        
        tickets_data["stats"]["open"] -= 1
        tickets_data["stats"]["closed"] += 1
        self.save_tickets_data()
        
        # Supprimer le salon après 5 secondes
        embed = discord.Embed(
            title="🎫 Ticket fermé",
            description=f"Ce ticket sera supprimé dans 5 secondes...\n**Fermé par:** {closer.mention}\n**Raison:** {reason}",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket #{ticket_id} fermé")
        
        # Log l'action
        await self.log_action(interaction.guild, "Ticket fermé", closer, f"Ticket #{ticket_id} - {reason}")
        
        log.info(f"🎫 Ticket #{ticket_id} fermé par {closer.display_name}")
        return True
    
    async def create_transcript(self, channel: discord.TextChannel) -> discord.File:
        """Crée un transcript du ticket"""
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
            content = message.content or "[Embed/File]"
            messages.append(f"[{timestamp}] {message.author.display_name}: {content}")
        
        transcript_content = "\n".join(messages)
        
        # Créer le fichier
        import io
        transcript_file = io.StringIO(transcript_content)
        return discord.File(transcript_file, filename=f"ticket-{channel.name}-transcript.txt")
    
    async def log_action(self, guild: discord.Guild, action: str, user: discord.Member, details: str):
        """Log les actions de tickets"""
        config = self.get_server_config(guild.id)
        log_channel_id = config.get("log_channel")
        
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title="🎫 Action Ticket",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="👤 Utilisateur", value=f"{user.mention} ({user.id})", inline=True)
                embed.add_field(name="⚡ Action", value=action, inline=True)
                embed.add_field(name="📝 Détails", value=details, inline=False)
                embed.set_footer(text=f"Arsenal Ticket System • {guild.name}")
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    log.error(f"❌ Erreur envoi log ticket: {e}")


class TicketControlView(discord.ui.View):
    """Boutons de contrôle pour les tickets"""
    
    def __init__(self, ticket_system: TicketSystem, ticket_id: int, creator_id: int):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
        self.creator_id = creator_id
    
    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier les permissions
        if interaction.user.id != self.creator_id and not interaction.user.guild_permissions.manage_channels:
            config = self.ticket_system.get_server_config(interaction.guild.id)
            user_role_ids = [role.id for role in interaction.user.roles]
            if not any(role_id in config["support_roles"] for role_id in user_role_ids):
                await interaction.response.send_message("❌ Vous n'avez pas la permission de fermer ce ticket", ephemeral=True)
                return
        
        # Demander confirmation
        embed = discord.Embed(
            title="🔒 Confirmer la fermeture",
            description="Êtes-vous sûr de vouloir fermer ce ticket ?",
            color=discord.Color.orange()
        )
        
        view = ConfirmCloseView(self.ticket_system, self.ticket_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📋 Transcript", style=discord.ButtonStyle.gray, custom_id="get_transcript")
    async def get_transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            transcript = await self.ticket_system.create_transcript(interaction.channel)
            await interaction.response.send_message("📋 Transcript du ticket:", file=transcript, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur création transcript: {e}", ephemeral=True)


class ConfirmCloseView(discord.ui.View):
    """Confirmation de fermeture de ticket"""
    
    def __init__(self, ticket_system: TicketSystem, ticket_id: int):
        super().__init__(timeout=30)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.red)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = await self.ticket_system.close_ticket(
            interaction, self.ticket_id, interaction.user, "Fermé via bouton"
        )
        if success:
            await interaction.response.send_message("🔒 Ticket fermé avec succès", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erreur lors de la fermeture", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.gray)
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Fermeture annulée", ephemeral=True)


class TicketPanelView(discord.ui.View):
    """Panel principal de création de tickets"""
    
    def __init__(self, ticket_system: TicketSystem):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @discord.ui.button(label="🆘 Support", style=discord.ButtonStyle.primary, custom_id="ticket_support")
    async def create_support_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "support")
    
    @discord.ui.button(label="🐛 Bug", style=discord.ButtonStyle.secondary, custom_id="ticket_bug")
    async def create_bug_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "bug")
    
    @discord.ui.button(label="💡 Suggestion", style=discord.ButtonStyle.success, custom_id="ticket_suggestion")
    async def create_suggestion_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "suggestion")
    
    @discord.ui.button(label="⚠️ Signalement", style=discord.ButtonStyle.danger, custom_id="ticket_report")
    async def create_report_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "report")
    
    async def _create_ticket(self, interaction: discord.Interaction, category: str):
        """Crée un ticket de la catégorie spécifiée"""
        config = self.ticket_system.get_server_config(interaction.guild.id)
        
        if not config["enabled"]:
            await interaction.response.send_message("❌ Le système de tickets est désactivé", ephemeral=True)
            return
        
        # Vérifier si l'utilisateur a trop de tickets ouverts
        tickets_data = self.ticket_system.get_server_tickets(interaction.guild.id)
        user_tickets = [t for t in tickets_data["tickets"].values() if t["user_id"] == interaction.user.id and t["status"] == "open"]
        
        if len(user_tickets) >= config["max_tickets_per_user"]:
            await interaction.response.send_message(f"❌ Vous avez déjà {len(user_tickets)} ticket(s) ouvert(s). Limite: {config['max_tickets_per_user']}", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Créer le ticket
        ticket_channel = await self.ticket_system.create_ticket(interaction, category, interaction.user)
        
        if ticket_channel:
            await interaction.followup.send(f"✅ Ticket créé: {ticket_channel.mention}", ephemeral=True)
        else:
            await interaction.followup.send("❌ Erreur lors de la création du ticket", ephemeral=True)


class TicketCog(commands.Cog):
    """Cog pour le système de tickets"""
    
    def __init__(self, bot):
        self.bot = bot
        self.ticket_system = TicketSystem(bot)
        
        # Ajouter les vues persistantes
        self.bot.add_view(TicketPanelView(self.ticket_system))
        self.bot.add_view(TicketControlView(self.ticket_system, 0, 0))  # Placeholder
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Met à jour l'activité des tickets"""
        if message.author.bot or not message.guild:
            return
        
        # Vérifier si c'est un salon de ticket
        tickets_data = self.ticket_system.get_server_tickets(message.guild.id)
        for ticket_data in tickets_data["tickets"].values():
            if ticket_data["channel_id"] == message.channel.id and ticket_data["status"] == "open":
                # Mettre à jour l'activité
                ticket_data["last_activity"] = datetime.now().isoformat()
                ticket_data["messages_count"] = ticket_data.get("messages_count", 0) + 1
                self.ticket_system.save_tickets_data()
                break


# Commandes slash pour les tickets
ticket_group = app_commands.Group(name="ticket", description="🎫 Système de tickets")

@ticket_group.command(name="setup", description="Configure le système de tickets")
@app_commands.describe(
    category="Catégorie pour les tickets",
    log_channel="Salon de logs (optionnel)"
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction, category: discord.CategoryChannel, log_channel: discord.TextChannel = None):
    cog = interaction.client.get_cog('TicketCog')
    if not cog:
        await interaction.response.send_message("❌ Système tickets non chargé", ephemeral=True)
        return
    
    config = cog.ticket_system.get_server_config(interaction.guild.id)
    config["category_id"] = category.id
    if log_channel:
        config["log_channel"] = log_channel.id
    
    cog.ticket_system.config["servers"][str(interaction.guild.id)] = config
    cog.ticket_system.save_config()
    
    embed = discord.Embed(
        title="✅ Système de Tickets Configuré",
        description=f"**Catégorie:** {category.mention}\n**Logs:** {log_channel.mention if log_channel else 'Aucun'}",
        color=discord.Color.green()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@ticket_group.command(name="panel", description="Crée le panel de tickets")
@app_commands.checks.has_permissions(administrator=True)
async def create_panel(interaction: discord.Interaction):
    cog = interaction.client.get_cog('TicketCog')
    if not cog:
        await interaction.response.send_message("❌ Système tickets non chargé", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎫 Arsenal Ticket System",
        description="Cliquez sur un bouton ci-dessous pour créer un ticket selon votre besoin.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🆘 Support Général",
        value="Besoin d'aide ou de support",
        inline=True
    )
    
    embed.add_field(
        name="🐛 Signaler un Bug",
        value="Problème technique à signaler",
        inline=True
    )
    
    embed.add_field(
        name="💡 Suggestion",
        value="Proposer une amélioration",
        inline=True
    )
    
    embed.add_field(
        name="⚠️ Signalement",
        value="Signaler un utilisateur",
        inline=True
    )
    
    embed.set_footer(text="Arsenal Bot • Un ticket = un salon privé avec l'équipe")
    
    view = TicketPanelView(cog.ticket_system)
    await interaction.response.send_message(embed=embed, view=view)

@ticket_group.command(name="close", description="Ferme le ticket actuel")
@app_commands.describe(reason="Raison de la fermeture")
async def close_ticket(interaction: discord.Interaction, reason: str = "Fermé par commande"):
    cog = interaction.client.get_cog('TicketCog')
    if not cog:
        await interaction.response.send_message("❌ Système tickets non chargé", ephemeral=True)
        return
    
    # Trouver le ticket correspondant au salon actuel
    tickets_data = cog.ticket_system.get_server_tickets(interaction.guild.id)
    ticket_id = None
    
    for tid, ticket_data in tickets_data["tickets"].items():
        if ticket_data["channel_id"] == interaction.channel.id and ticket_data["status"] == "open":
            ticket_id = int(tid)
            break
    
    if not ticket_id:
        await interaction.response.send_message("❌ Ce salon n'est pas un ticket ouvert", ephemeral=True)
        return
    
    success = await cog.ticket_system.close_ticket(interaction, ticket_id, interaction.user, reason)
    if success:
        await interaction.response.send_message("🔒 Ticket fermé avec succès", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Erreur lors de la fermeture", ephemeral=True)

@ticket_group.command(name="stats", description="Affiche les statistiques des tickets")
async def ticket_stats(interaction: discord.Interaction):
    cog = interaction.client.get_cog('TicketCog')
    if not cog:
        await interaction.response.send_message("❌ Système tickets non chargé", ephemeral=True)
        return
    
    tickets_data = cog.ticket_system.get_server_tickets(interaction.guild.id)
    stats = tickets_data["stats"]
    
    embed = discord.Embed(
        title="📊 Statistiques Tickets",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="📝 Total", value=stats["total"], inline=True)
    embed.add_field(name="🟢 Ouverts", value=stats["open"], inline=True)
    embed.add_field(name="🔴 Fermés", value=stats["closed"], inline=True)
    
    # Statistiques par catégorie
    categories = {}
    for ticket_data in tickets_data["tickets"].values():
        cat = ticket_data["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    if categories:
        cat_text = "\n".join([f"**{cat}:** {count}" for cat, count in categories.items()])
        embed.add_field(name="📋 Par catégorie", value=cat_text, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Setup du cog tickets"""
    await bot.add_cog(TicketCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(ticket_group)
    
    log.info("🎫 Système Tickets chargé avec succès")
