#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎧 ARSENAL V4 - SYSTÈME HUB VOCAL ULTRA-AVANCÉ
Création/gestion salons temporaires, panels de configuration, gestion permissions
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

class VoiceHubSystem:
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/voice_hub_config.json"
        self.temp_channels = {}  # Cache des salons temporaires actifs
        self.load_config()
        
        # Démarrer la tâche de nettoyage automatique
        self.cleanup_task = bot.loop.create_task(self.auto_cleanup_loop())
        
        # Récupérer les salons temporaires existants au démarrage
        bot.loop.create_task(self.restore_temp_channels_on_startup())
        
    def load_config(self):
        """Charge la configuration des hubs vocaux"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                log.info("🎧 Configuration voice hub chargée")
            except Exception as e:
                log.error(f"❌ Erreur chargement voice hub config: {e}")
                self.config = {"servers": {}}
        else:
            self.config = {"servers": {}}
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            log.info("💾 Configuration voice hub sauvegardée")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde voice hub: {e}")
    
    def get_server_hubs(self, guild_id: int) -> dict:
        """Récupère les hubs d'un serveur"""
        guild_id = str(guild_id)
        if guild_id not in self.config["servers"]:
            self.config["servers"][guild_id] = {"hubs": {}}
            self.save_config()
        return self.config["servers"][guild_id].get("hubs", {})
    
    def create_hub(self, guild_id: int, hub_channel_id: int, category_id: int, creator_id: int, name: str) -> dict:
        """Crée un nouveau hub vocal"""
        guild_id = str(guild_id)
        hub_id = str(hub_channel_id)
        
        if guild_id not in self.config["servers"]:
            self.config["servers"][guild_id] = {"hubs": {}}
        
        hub_config = {
            "name": name,
            "hub_channel_id": hub_channel_id,
            "category_id": category_id,
            "creator_id": creator_id,
            "created_at": datetime.now().isoformat(),
            "settings": {
                "auto_delete_empty": True,
                "max_temp_channels": 10,
                "channel_name_template": "{username}'s Channel",
                "default_user_limit": 0,  # 0 = pas de limite
                "auto_move_creator": True,
                "temp_channel_prefix": "🎧"
            },
            "permissions": {
                "moderators": [],  # IDs des modérateurs
                "allowed_roles": [],  # Rôles autorisés
                "banned_users": []  # Utilisateurs bannis
            },
            "temp_channels": {}  # Salons temporaires actifs
        }
        
        self.config["servers"][guild_id]["hubs"][hub_id] = hub_config
        self.save_config()
        return hub_config
    
    def get_hub_config(self, guild_id: int, hub_channel_id: int) -> Optional[dict]:
        """Récupère la config d'un hub spécifique"""
        hubs = self.get_server_hubs(guild_id)
        return hubs.get(str(hub_channel_id))
    
    def update_hub_config(self, guild_id: int, hub_channel_id: int, new_config: dict):
        """Met à jour la config d'un hub"""
        guild_id = str(guild_id)
        hub_id = str(hub_channel_id)
        
        if guild_id in self.config["servers"] and hub_id in self.config["servers"][guild_id]["hubs"]:
            self.config["servers"][guild_id]["hubs"][hub_id] = new_config
            self.save_config()
    
    async def create_temp_channel(self, member: discord.Member, hub_config: dict) -> Optional[discord.VoiceChannel]:
        """Crée un salon vocal temporaire avec chat textuel intégré"""
        guild = member.guild
        category_id = hub_config["category_id"]
        category = guild.get_channel(category_id)
        
        if not category or not isinstance(category, discord.CategoryChannel):
            log.error(f"❌ Catégorie {category_id} introuvable pour hub")
            return None
        
        # Vérifier la limite de salons temporaires
        active_temp_channels = len([ch for ch in category.voice_channels if ch.id != hub_config["hub_channel_id"]])
        if active_temp_channels >= hub_config["settings"]["max_temp_channels"]:
            return None
        
        # Générer le nom du salon
        name_template = hub_config["settings"]["channel_name_template"]
        channel_name = name_template.format(
            username=member.display_name,
            user=member.display_name,
            prefix=hub_config["settings"]["temp_channel_prefix"]
        )
        
        try:
            # Créer le salon vocal temporaire simple (sans chat textuel séparé)
            temp_channel = await category.create_voice_channel(
                name=f"🎧 {channel_name}",
                user_limit=hub_config["settings"]["default_user_limit"],
                reason=f"Salon temporaire créé par {member.display_name}"
            )
            
            # Donner les permissions au créateur
            owner_perms = discord.PermissionOverwrite(
                manage_channels=True,
                manage_permissions=True,
                move_members=True,
                mute_members=True,
                deafen_members=True
            )
            
            await temp_channel.set_permissions(member, overwrite=owner_perms)
            
            # Déplacer le membre dans son salon
            if hub_config["settings"]["auto_move_creator"]:
                await member.move_to(temp_channel)
            
            # Enregistrer le salon temporaire
            temp_channel_data = {
                "channel_id": temp_channel.id,
                "owner_id": member.id,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            }
            
            hub_config["temp_channels"][str(temp_channel.id)] = temp_channel_data
            self.update_hub_config(guild.id, hub_config["hub_channel_id"], hub_config)
            
            # Ajouter au cache local
            self.temp_channels[temp_channel.id] = {
                "owner_id": member.id,
                "hub_channel_id": hub_config["hub_channel_id"],
                "guild_id": guild.id
            }
            
            log.info(f"🎧 Salon temporaire créé: {channel_name} pour {member.display_name}")
            
            # Envoyer le panel de contrôle en DM au propriétaire
            await self.send_dm_control_panel(temp_channel, member)
            
            return temp_channel
            
        except Exception as e:
            log.error(f"❌ Erreur création salon temporaire: {e}")
            return None
    
    async def send_dm_control_panel(self, voice_channel: discord.VoiceChannel, owner: discord.Member):
        """Envoie le panel de contrôle en DM au propriétaire"""
        try:
            from modules.voice_control_panel import VoiceControlView
            
            # Message de bienvenue
            welcome_embed = discord.Embed(
                title="🎉 Salon Vocal Créé avec Succès !",
                description=f"Salut {owner.mention} ! 👋\n\nVotre salon vocal temporaire **{voice_channel.name}** a été créé !",
                color=discord.Color.green()
            )
            
            welcome_embed.add_field(
                name="🏠 Votre Zone de Confort",
                value=(
                    f"🎧 **Salon Vocal:** {voice_channel.mention}\n"
                    f"🎮  **Contrôles:** Panel ci-dessous\n"
                    f"💡 **Astuce:** Rejoignez votre salon pour l'utiliser !"
                ),
                inline=False
            )
            
            # Panel de contrôle principal
            control_embed = discord.Embed(
                title="🎮 Panneau de Contrôle - Salon Temporaire",
                description=f"**🏠 Propriétaire:** {owner.mention}\n**🎧 Salon Vocal:** {voice_channel.mention}",
                color=discord.Color.blue()
            )
            
            control_embed.add_field(
                name="🎯 Zone de Contrôle Personnelle",
                value=(
                    "🔒 **Verrouiller/Déverrouiller** - Contrôler l'accès\n"
                    "👁️ **Masquer/Montrer** - Visibilité du salon\n"
                    "👥 **Limite** - Nombre max d'utilisateurs\n"
                    "✏️ **Renommer** - Changer le nom du salon\n"
                    "🔄 **Transférer** - Donner la propriété"
                ),
                inline=False
            )
            
            control_embed.add_field(
                name="🛡️ Gestion des Accès",
                value=(
                    "➕ **Whitelist** - Utilisateurs autorisés\n"
                    "➖ **Blacklist** - Utilisateurs interdits\n"
                    "🎭 **Rôle Temp** - Créer un rôle temporaire\n"
                    "👢 **Expulser** - Retirer quelqu'un du salon\n"
                    "🗑️ **Supprimer** - Fermer définitivement"
                ),
                inline=False
            )
            
            control_embed.add_field(
                name="💡 Informations",
                value=(
                    "• **Contrôle Total:** Vous avez tous les droits sur votre salon\n"
                    "• **Rôles Temporaires:** Se suppriment à la fermeture\n"
                    "• **Listes d'Accès:** Whitelist/Blacklist personnalisables\n"
                    "• **Suppression Auto:** Le salon se ferme quand il est vide"
                ),
                inline=False
            )
            
            control_embed.set_footer(text="🎧 Arsenal Voice Hub • Votre espace de confort vocal", icon_url=owner.avatar.url if owner.avatar else None)
            control_embed.set_thumbnail(url=voice_channel.guild.icon.url if voice_channel.guild.icon else None)
            
            # Créer la vue avec boutons interactifs
            control_view = VoiceControlView(voice_channel, voice_channel, owner)  # Utiliser le voice_channel comme "text_channel"
            
            # Envoyer les messages en DM
            await owner.send(embed=welcome_embed)
            await owner.send(embed=control_embed, view=control_view)
            
            log.info(f"🎮 Panel de contrôle envoyé en DM à {owner.display_name}")
            
        except discord.Forbidden:
            log.warning(f"⚠️ Impossible d'envoyer DM à {owner.display_name}, DMs fermés")
        except Exception as e:
            log.error(f"❌ Erreur envoi panel de contrôle en DM: {e}")
    
    async def send_control_panel(self, channel: discord.VoiceChannel, owner: discord.Member):
        """Envoie le panel de contrôle du salon temporaire"""
        embed = discord.Embed(
            title="🎧 Panel de Contrôle - Salon Temporaire",
            description=f"**Propriétaire:** {owner.mention}\n**Salon:** {channel.mention}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔧 Commandes disponibles",
            value=(
                "`/voice rename <nom>` - Renommer le salon\n"
                "`/voice limit <nombre>` - Limite d'utilisateurs\n"
                "`/voice lock` - Verrouiller le salon\n"
                "`/voice unlock` - Déverrouiller le salon\n"
                "`/voice kick <user>` - Expulser un utilisateur\n"
                "`/voice transfer <user>` - Transférer la propriété\n"
                "`/voice delete` - Supprimer le salon"
            ),
            inline=False
        )
        
        embed.set_footer(text="Ce salon sera supprimé automatiquement s'il reste vide pendant 5 minutes")
        
        # Trouver un salon texte pour envoyer le message
        text_channels = [ch for ch in channel.guild.text_channels if ch.permissions_for(channel.guild.me).send_messages]
        if text_channels:
            # Prioriser un salon "général" ou similaire
            target_channel = None
            for ch in text_channels:
                if any(keyword in ch.name.lower() for keyword in ['général', 'general', 'chat', 'salon']):
                    target_channel = ch
                    break
            
            if not target_channel:
                target_channel = text_channels[0]
            
            try:
                await target_channel.send(f"{owner.mention}", embed=embed, delete_after=300)  # Supprime après 5 min
            except Exception as e:
                log.warning(f"⚠️ Impossible d'envoyer le panel de contrôle: {e}")
    
    async def delete_temp_channel(self, channel_id: int, reason: str = "Salon vide"):
        """Supprime un salon temporaire"""
        if channel_id in self.temp_channels:
            temp_data = self.temp_channels[channel_id]
            guild_id = temp_data["guild_id"]
            hub_channel_id = temp_data["hub_channel_id"]
            
            # Supprimer de la config
            hub_config = self.get_hub_config(guild_id, hub_channel_id)
            if hub_config and str(channel_id) in hub_config["temp_channels"]:
                del hub_config["temp_channels"][str(channel_id)]
                self.update_hub_config(guild_id, hub_channel_id, hub_config)
            
            # Supprimer du cache
            del self.temp_channels[channel_id]
            
            # Supprimer le salon Discord
            guild = self.bot.get_guild(guild_id)
            if guild:
                voice_channel = guild.get_channel(channel_id)
                if voice_channel:
                    try:
                        await voice_channel.delete(reason=f"Arsenal Hub: {reason}")
                        log.info(f"🗑️ Salon vocal supprimé: {voice_channel.name} ({reason})")
                    except Exception as e:
                        log.error(f"❌ Erreur suppression salon vocal: {e}")
    
    async def check_empty_channels(self):
        """Vérifie et supprime les salons vides"""
        to_delete = []
        
        for channel_id, temp_data in self.temp_channels.items():
            guild = self.bot.get_guild(temp_data["guild_id"])
            if not guild:
                to_delete.append(channel_id)
                continue
            
            channel = guild.get_channel(channel_id)
            if not channel:
                to_delete.append(channel_id)
                continue
            
            # Vérifier si le salon est vide
            if len(channel.members) == 0:
                # Attendre 5 minutes avant suppression
                hub_config = self.get_hub_config(temp_data["guild_id"], temp_data["hub_channel_id"])
                if hub_config:
                    temp_channel_data = hub_config["temp_channels"].get(str(channel_id))
                    if temp_channel_data:
                        last_activity = datetime.fromisoformat(temp_channel_data["last_activity"])
                        if datetime.now() - last_activity > timedelta(minutes=5):
                            to_delete.append(channel_id)
        
        # Supprimer les salons identifiés
        for channel_id in to_delete:
            await self.delete_temp_channel(channel_id, "Inactif pendant 5+ minutes")
    
    async def is_hub_manager(self, member: discord.Member, hub_config: dict) -> bool:
        """Vérifie si un membre peut gérer le hub"""
        if member.guild_permissions.administrator:
            return True
        
        if member.id == hub_config["creator_id"]:
            return True
        
        if member.id in hub_config["permissions"]["moderators"]:
            return True
        
        return False
    
    async def can_use_hub(self, member: discord.Member, hub_config: dict) -> bool:
        """Vérifie si un membre peut utiliser le hub"""
        if member.id in hub_config["permissions"]["banned_users"]:
            return False
        
        if await self.is_hub_manager(member, hub_config):
            return True
        
        allowed_roles = hub_config["permissions"]["allowed_roles"]
        if allowed_roles:
            user_role_ids = [role.id for role in member.roles]
            if not any(role_id in allowed_roles for role_id in user_role_ids):
                return False
        
        return True


class VoiceHubCog(commands.Cog):
    """Cog pour le système de hub vocal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_hub = VoiceHubSystem(bot)
        
        # Tâche de nettoyage des salons vides
        self.cleanup_task = asyncio.create_task(self.cleanup_loop())
    
    async def cleanup_loop(self):
        """Boucle de nettoyage des salons vides"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await self.voice_hub.check_empty_channels()
                await asyncio.sleep(60)  # Vérifier toutes les minutes
            except Exception as e:
                log.error(f"❌ Erreur cleanup loop: {e}")
                await asyncio.sleep(60)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Gère les changements d'état vocal"""
        # Membre rejoint un salon hub
        if after.channel:
            hub_config = self.voice_hub.get_hub_config(member.guild.id, after.channel.id)
            if hub_config:
                # Vérifier les permissions
                if not await self.voice_hub.can_use_hub(member, hub_config):
                    # Déconnecter le membre s'il n'a pas les permissions
                    try:
                        await member.move_to(None)
                        # Envoyer un message privé si possible
                        try:
                            await member.send("❌ Vous n'avez pas l'autorisation d'utiliser ce hub vocal.")
                        except:
                            pass
                    except:
                        pass
                    return
                
                # Créer un salon temporaire
                temp_channel = await self.voice_hub.create_temp_channel(member, hub_config)
                if not temp_channel:
                    # Échec de création, notifier l'utilisateur
                    try:
                        await member.send("❌ Impossible de créer un salon temporaire. Limite atteinte ou erreur.")
                    except:
                        pass
        
        # Mise à jour de l'activité des salons temporaires
        if before.channel and before.channel.id in self.voice_hub.temp_channels:
            # Mettre à jour l'heure de dernière activité
            temp_data = self.voice_hub.temp_channels[before.channel.id]
            hub_config = self.voice_hub.get_hub_config(temp_data["guild_id"], temp_data["hub_channel_id"])
            if hub_config and str(before.channel.id) in hub_config["temp_channels"]:
                hub_config["temp_channels"][str(before.channel.id)]["last_activity"] = datetime.now().isoformat()
                self.voice_hub.update_hub_config(temp_data["guild_id"], temp_data["hub_channel_id"], hub_config)
        
        if after.channel and after.channel.id in self.voice_hub.temp_channels:
            # Mettre à jour l'heure de dernière activité
            temp_data = self.voice_hub.temp_channels[after.channel.id]
            hub_config = self.voice_hub.get_hub_config(temp_data["guild_id"], temp_data["hub_channel_id"])
            if hub_config and str(after.channel.id) in hub_config["temp_channels"]:
                hub_config["temp_channels"][str(after.channel.id)]["last_activity"] = datetime.now().isoformat()
                self.voice_hub.update_hub_config(temp_data["guild_id"], temp_data["hub_channel_id"], hub_config)


# Commandes slash pour les hubs vocaux
voice_hub_group = app_commands.Group(name="hub", description="🎧 Gestion des hubs vocaux")
voice_control_group = app_commands.Group(name="voice", description="🔧 Contrôle des salons temporaires")

@voice_hub_group.command(name="create", description="Crée un hub vocal")
@app_commands.describe(
    name="Nom du hub vocal",
    channel="Canal vocal à utiliser comme hub (optionnel)",
    category="Catégorie pour les salons temporaires (optionnel)"
)
@app_commands.checks.has_permissions(administrator=True)
async def create_hub(interaction: discord.Interaction, name: str, channel: discord.VoiceChannel = None, category: discord.CategoryChannel = None):
    cog = interaction.client.get_cog('VoiceHubCog')
    if not cog:
        await interaction.response.send_message("❌ Système voice hub non chargé", ephemeral=True)
        return
    
    guild = interaction.guild
    
    # Si pas de salon spécifié, créer un nouveau
    if not channel:
        # Si pas de catégorie spécifiée, créer une nouvelle
        if not category:
            category = await guild.create_category(f"🎧 {name}")
        
        # Créer le salon hub
        channel = await category.create_voice_channel(f"➕ Rejoindre {name}")
    else:
        # Utiliser la catégorie du salon existant
        if not category:
            category = channel.category
            if not category:
                await interaction.response.send_message("❌ Le salon vocal doit être dans une catégorie", ephemeral=True)
                return
    
    # Créer la configuration du hub
    hub_config = cog.voice_hub.create_hub(
        guild_id=guild.id,
        hub_channel_id=channel.id,
        category_id=category.id,
        creator_id=interaction.user.id,
        name=name
    )
    
    embed = discord.Embed(
        title="✅ Hub Vocal Créé",
        description=f"**Hub:** {name}\n**Canal:** {channel.mention}\n**Catégorie:** {category.mention}",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="🎧 Fonctionnement",
        value="Les utilisateurs qui rejoignent ce salon obtiendront automatiquement leur propre salon temporaire dans la catégorie.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@voice_hub_group.command(name="list", description="Liste les hubs vocaux du serveur")
async def list_hubs(interaction: discord.Interaction):
    cog = interaction.client.get_cog('VoiceHubCog')
    if not cog:
        await interaction.response.send_message("❌ Système voice hub non chargé", ephemeral=True)
        return
    
    hubs = cog.voice_hub.get_server_hubs(interaction.guild.id)
    
    if not hubs:
        await interaction.response.send_message("📭 Aucun hub vocal configuré sur ce serveur", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎧 Hubs Vocaux",
        description=f"**{len(hubs)} hub(s) configuré(s)**",
        color=discord.Color.blue()
    )
    
    for hub_id, hub_config in hubs.items():
        channel = interaction.guild.get_channel(int(hub_id))
        channel_mention = channel.mention if channel else f"Canal supprimé ({hub_id})"
        
        active_temp = len(hub_config["temp_channels"])
        max_temp = hub_config["settings"]["max_temp_channels"]
        
        embed.add_field(
            name=f"🎧 {hub_config['name']}",
            value=f"**Canal:** {channel_mention}\n**Salons actifs:** {active_temp}/{max_temp}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@voice_hub_group.command(name="delete", description="Supprime un hub vocal")
@app_commands.describe(channel="Canal hub à supprimer")
@app_commands.checks.has_permissions(administrator=True)
async def delete_hub(interaction: discord.Interaction, channel: discord.VoiceChannel):
    cog = interaction.client.get_cog('VoiceHubCog')
    if not cog:
        await interaction.response.send_message("❌ Système voice hub non chargé", ephemeral=True)
        return
    
    hub_config = cog.voice_hub.get_hub_config(interaction.guild.id, channel.id)
    if not hub_config:
        await interaction.response.send_message("❌ Ce salon n'est pas configuré comme hub vocal", ephemeral=True)
        return
    
    # Supprimer tous les salons temporaires
    temp_channels = list(hub_config["temp_channels"].keys())
    for temp_channel_id in temp_channels:
        await cog.voice_hub.delete_temp_channel(int(temp_channel_id), "Hub supprimé")
    
    # Supprimer le hub de la config
    guild_id = str(interaction.guild.id)
    hub_id = str(channel.id)
    del cog.voice_hub.config["servers"][guild_id]["hubs"][hub_id]
    cog.voice_hub.save_config()
    
    await interaction.response.send_message(f"✅ Hub vocal {channel.mention} supprimé", ephemeral=True)

# Commandes de contrôle des salons temporaires
@voice_control_group.command(name="rename", description="Renomme votre salon temporaire")
@app_commands.describe(name="Nouveau nom du salon")
async def rename_temp_channel(interaction: discord.Interaction, name: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Vous devez être dans un salon vocal", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    cog = interaction.client.get_cog('VoiceHubCog')
    
    if channel.id not in cog.voice_hub.temp_channels:
        await interaction.response.send_message("❌ Ce n'est pas un salon temporaire", ephemeral=True)
        return
    
    temp_data = cog.voice_hub.temp_channels[channel.id]
    if interaction.user.id != temp_data["owner_id"]:
        await interaction.response.send_message("❌ Seul le propriétaire peut renommer le salon", ephemeral=True)
        return
    
    try:
        old_name = channel.name
        await channel.edit(name=name)
        await interaction.response.send_message(f"✅ Salon renommé: `{old_name}` → `{name}`", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

@voice_control_group.command(name="limit", description="Définit la limite d'utilisateurs")
@app_commands.describe(limit="Nombre max d'utilisateurs (0 = pas de limite)")
async def limit_temp_channel(interaction: discord.Interaction, limit: int):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Vous devez être dans un salon vocal", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    cog = interaction.client.get_cog('VoiceHubCog')
    
    if channel.id not in cog.voice_hub.temp_channels:
        await interaction.response.send_message("❌ Ce n'est pas un salon temporaire", ephemeral=True)
        return
    
    temp_data = cog.voice_hub.temp_channels[channel.id]
    if interaction.user.id != temp_data["owner_id"]:
        await interaction.response.send_message("❌ Seul le propriétaire peut modifier la limite", ephemeral=True)
        return
    
    if limit < 0 or limit > 99:
        await interaction.response.send_message("❌ La limite doit être entre 0 et 99", ephemeral=True)
        return
    
    try:
        await channel.edit(user_limit=limit)
        limit_text = f"{limit} utilisateurs" if limit > 0 else "aucune limite"
        await interaction.response.send_message(f"✅ Limite définie: {limit_text}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

@voice_control_group.command(name="lock", description="Verrouille votre salon temporaire")
async def lock_temp_channel(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Vous devez être dans un salon vocal", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    cog = interaction.client.get_cog('VoiceHubCog')
    
    if channel.id not in cog.voice_hub.temp_channels:
        await interaction.response.send_message("❌ Ce n'est pas un salon temporaire", ephemeral=True)
        return
    
    temp_data = cog.voice_hub.temp_channels[channel.id]
    if interaction.user.id != temp_data["owner_id"]:
        await interaction.response.send_message("❌ Seul le propriétaire peut verrouiller le salon", ephemeral=True)
        return
    
    try:
        # Bloquer l'accès pour @everyone
        overwrite = discord.PermissionOverwrite(connect=False)
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔒 Salon verrouillé", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

@voice_control_group.command(name="unlock", description="Déverrouille votre salon temporaire")
async def unlock_temp_channel(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Vous devez être dans un salon vocal", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    cog = interaction.client.get_cog('VoiceHubCog')
    
    if channel.id not in cog.voice_hub.temp_channels:
        await interaction.response.send_message("❌ Ce n'est pas un salon temporaire", ephemeral=True)
        return
    
    temp_data = cog.voice_hub.temp_channels[channel.id]
    if interaction.user.id != temp_data["owner_id"]:
        await interaction.response.send_message("❌ Seul le propriétaire peut déverrouiller le salon", ephemeral=True)
        return
    
    try:
        # Rétablir l'accès pour @everyone
        await channel.set_permissions(interaction.guild.default_role, overwrite=None)
        await interaction.response.send_message("🔓 Salon déverrouillé", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

@voice_control_group.command(name="kick", description="Expulse un utilisateur de votre salon")
@app_commands.describe(user="Utilisateur à expulser")
async def kick_from_temp_channel(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Vous devez être dans un salon vocal", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    cog = interaction.client.get_cog('VoiceHubCog')
    
    if channel.id not in cog.voice_hub.temp_channels:
        await interaction.response.send_message("❌ Ce n'est pas un salon temporaire", ephemeral=True)
        return
    
    temp_data = cog.voice_hub.temp_channels[channel.id]
    if interaction.user.id != temp_data["owner_id"]:
        await interaction.response.send_message("❌ Seul le propriétaire peut expulser des utilisateurs", ephemeral=True)
        return
    
    if user.voice and user.voice.channel == channel:
        try:
            await user.move_to(None)
            await interaction.response.send_message(f"👢 {user.mention} expulsé du salon", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Cet utilisateur n'est pas dans votre salon", ephemeral=True)

@voice_control_group.command(name="delete", description="Supprime votre salon temporaire")
async def delete_temp_channel(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Vous devez être dans un salon vocal", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    cog = interaction.client.get_cog('VoiceHubCog')
    
    if channel.id not in cog.voice_hub.temp_channels:
        await interaction.response.send_message("❌ Ce n'est pas un salon temporaire", ephemeral=True)
        return
    
    temp_data = cog.voice_hub.temp_channels[channel.id]
    if interaction.user.id != temp_data["owner_id"]:
        await interaction.response.send_message("❌ Seul le propriétaire peut supprimer le salon", ephemeral=True)
        return
    
    await interaction.response.send_message("🗑️ Suppression du salon...", ephemeral=True)
    await cog.voice_hub.delete_temp_channel(channel.id, "Supprimé par le propriétaire")

    async def auto_cleanup_loop(self):
        """Boucle de nettoyage automatique des salons vides"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                await self.check_empty_channels()
                await asyncio.sleep(60)  # Vérifier toutes les minutes
            except Exception as e:
                log.error(f"❌ Erreur dans la boucle de nettoyage: {e}")
                await asyncio.sleep(60)
    
    async def restore_temp_channels_on_startup(self):
        """Restore les salons temporaires depuis la config au démarrage du bot"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)  # Attendre que le bot soit complètement prêt
        
        try:
            for guild_id_str, server_data in self.config.get("servers", {}).items():
                guild_id = int(guild_id_str)
                guild = self.bot.get_guild(guild_id)
                
                if not guild:
                    continue
                
                for hub_channel_id_str, hub_config in server_data.get("hubs", {}).items():
                    hub_channel_id = int(hub_channel_id_str)
                    
                    # Restaurer les salons temporaires de ce hub
                    for temp_channel_id_str, temp_data in hub_config.get("temp_channels", {}).items():
                        temp_channel_id = int(temp_channel_id_str)
                        
                        # Vérifier si le salon existe encore
                        temp_channel = guild.get_channel(temp_channel_id)
                        if temp_channel:
                            # Ajouter au cache
                            self.temp_channels[temp_channel_id] = {
                                "owner_id": temp_data["owner_id"],
                                "hub_channel_id": hub_channel_id,
                                "guild_id": guild_id
                            }
                            log.info(f"🔄 Salon temporaire restauré: {temp_channel.name}")
                        else:
                            # Salon supprimé manuellement, nettoyer la config
                            log.warning(f"🧹 Nettoyage salon temporaire inexistant: {temp_channel_id}")
                            del hub_config["temp_channels"][temp_channel_id_str]
            
            # Sauvegarder les changements si des salons ont été nettoyés
            self.save_config()
            log.info("✅ Restauration des salons temporaires terminée")
            
        except Exception as e:
            log.error(f"❌ Erreur restauration salons temporaires: {e}")

    async def on_voice_state_update_handler(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Gestionnaire pour les changements d'état vocal (intégré au système)"""
        # Si quelqu'un rejoint un salon temporaire, envoyer un message de bienvenue
        if after.channel and after.channel.id in self.temp_channels:
            temp_data = self.temp_channels[after.channel.id]
            
            # Si c'est le propriétaire qui rejoint, envoyer le panel de contrôle
            if member.id == temp_data["owner_id"]:
                try:
                    # Envoyer un DM avec le panel de contrôle
                    from modules.voice_control_panel import VoiceControlView
                    
                    welcome_embed = discord.Embed(
                        title="🎧 Bienvenue dans votre Salon Vocal !",
                        description=f"Salut {member.mention} ! 👋\n\nVous êtes maintenant dans votre salon vocal temporaire **{after.channel.name}**",
                        color=discord.Color.green()
                    )
                    
                    welcome_embed.add_field(
                        name="🎮 Contrôles disponibles",
                        value=(
                            "🔒 **Verrouiller/Déverrouiller** - Contrôler l'accès\n"
                            "👁️ **Masquer/Montrer** - Visibilité du salon\n"
                            "👥 **Limite** - Nombre max d'utilisateurs\n"
                            "✏️ **Renommer** - Changer le nom du salon\n"
                            "🔄 **Transférer** - Donner la propriété\n"
                            "➕ **Whitelist** - Utilisateurs autorisés\n"
                            "➖ **Blacklist** - Utilisateurs interdits\n"
                            "🎭 **Rôle Temp** - Créer un rôle temporaire\n"
                            "👢 **Expulser** - Retirer quelqu'un du salon\n"
                            "🗑️ **Supprimer** - Fermer définitivement"
                        ),
                        inline=False
                    )
                    
                    control_view = VoiceControlView(after.channel, after.channel, member)  # On utilise le salon vocal comme "text_channel"
                    
                    # Envoyer en DM
                    await member.send(embed=welcome_embed, view=control_view)
                    
                except Exception as e:
                    log.error(f"❌ Erreur envoi panel de contrôle en DM: {e}")
            else:
                # Simple message de bienvenue pour les autres
                try:
                    owner = member.guild.get_member(temp_data["owner_id"])
                    owner_name = owner.display_name if owner else "Propriétaire"
                    
                    welcome_msg = f"👋 Bienvenue {member.mention} dans le salon de **{owner_name}** !"
                    
                    # Envoyer un message temporaire dans le salon vocal (ne fonctionne pas directement)
                    # On peut essayer d'envoyer en DM à l'utilisateur
                    welcome_embed = discord.Embed(
                        title="👋 Bienvenue !",
                        description=f"Vous avez rejoint le salon vocal de **{owner_name}**\n\n🎧 **{after.channel.name}**",
                        color=discord.Color.blue()
                    )
                    
                    try:
                        await member.send(embed=welcome_embed)
                    except:
                        pass  # L'utilisateur a peut-être désactivé les DMs
                        
                except Exception as e:
                    log.error(f"❌ Erreur message de bienvenue: {e}")


async def setup(bot):
    """Setup du cog voice hub"""
    await bot.add_cog(VoiceHubCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(voice_hub_group)
    bot.tree.add_command(voice_control_group)
    
    log.info("🎧 Système Voice Hub chargé avec succès")
