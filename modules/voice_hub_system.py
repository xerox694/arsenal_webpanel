#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎧 ARSENAL V4 - SYSTÈME HUB VOCAL ULTRA-AVANCÉ (VERSION PROPRE)
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
        
        # Démarrer les tâches de nettoyage automatique
        bot.loop.create_task(self.restore_temp_channels_on_startup())
        bot.loop.create_task(self.auto_cleanup_loop())
        
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
    
    def get_hub_config(self, guild_id: int, hub_channel_id: int) -> Optional[dict]:
        """Récupère la configuration d'un hub spécifique"""
        hubs = self.get_server_hubs(guild_id)
        return hubs.get(str(hub_channel_id))
    
    def update_hub_config(self, guild_id: int, hub_channel_id: int, new_config: dict):
        """Met à jour la configuration d'un hub"""
        hubs = self.get_server_hubs(guild_id)
        hubs[str(hub_channel_id)] = new_config
        self.save_config()
    
    async def can_use_hub(self, member: discord.Member, hub_config: dict) -> bool:
        """Vérifie si un membre peut utiliser le hub"""
        if member.guild_permissions.administrator:
            return True
        
        permissions = hub_config.get("permissions", {})
        
        # Vérifier les rôles autorisés
        allowed_roles = permissions.get("allowed_roles", [])
        if allowed_roles:
            member_role_ids = [role.id for role in member.roles]
            if not any(role_id in member_role_ids for role_id in allowed_roles):
                return False
        
        # Vérifier les utilisateurs bannis
        banned_users = permissions.get("banned_users", [])
        if member.id in banned_users:
            return False
        
        return True
    
    async def create_temp_channel(self, member: discord.Member, hub_config: dict) -> Optional[discord.VoiceChannel]:
        """Crée un salon vocal temporaire simple (avec panel DM)"""
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
            # Créer le salon vocal temporaire simple
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


class VoiceHubCog(commands.Cog):
    """Cog pour le système de hub vocal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_hub = VoiceHubSystem(bot)
    
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


@app_commands.command(name="hub_create", description="🎧 Créer un hub vocal temporaire")
@app_commands.describe(
    channel="Le salon vocal qui servira de hub",
    category="La catégorie où créer les salons temporaires",
    name_template="Template du nom des salons (ex: {username}'s Channel)"
)
async def hub_create(interaction: discord.Interaction, channel: discord.VoiceChannel, category: discord.CategoryChannel, name_template: str = "{username}'s Channel"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Seuls les administrateurs peuvent créer des hubs", ephemeral=True)
        return
    
    # Récupérer le système voice hub
    cog = interaction.client.get_cog("VoiceHubCog")
    if not cog:
        await interaction.response.send_message("❌ Système voice hub non disponible", ephemeral=True)
        return
    
    # Configuration par défaut du hub
    hub_config = {
        "hub_channel_id": channel.id,
        "category_id": category.id,
        "creator_id": interaction.user.id,
        "created_at": datetime.now().isoformat(),
        "settings": {
            "channel_name_template": name_template,
            "temp_channel_prefix": "🎧",
            "max_temp_channels": 20,
            "default_user_limit": 0,
            "auto_move_creator": True,
            "delete_empty_after": 300  # 5 minutes
        },
        "permissions": {
            "allowed_roles": [],
            "banned_users": [],
            "moderators": []
        },
        "temp_channels": {}
    }
    
    # Sauvegarder la configuration
    cog.voice_hub.update_hub_config(interaction.guild.id, channel.id, hub_config)
    
    # Message de confirmation
    embed = discord.Embed(
        title="🎧 Hub Vocal Créé !",
        description=f"Le hub vocal a été configuré avec succès !",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="📋 Configuration",
        value=(
            f"🎧 **Hub Channel:** {channel.mention}\n"
            f"📁 **Catégorie:** {category.name}\n"
            f"🏷️ **Template:** {name_template}\n"
            f"🔢 **Limite salons:** 20\n"
            f"👥 **Limite utilisateurs:** Illimité"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🚀 Comment ça marche ?",
        value=(
            "1️⃣ Les utilisateurs rejoignent le salon hub\n"
            "2️⃣ Un salon temporaire est créé automatiquement\n"
            "3️⃣ Le propriétaire reçoit un panel de contrôle en DM\n"
            "4️⃣ Le salon se supprime automatiquement quand il est vide"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup du cog voice hub"""
    await bot.add_cog(VoiceHubCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(hub_create)
    
    log.info("🎧 Système Voice Hub chargé avec succès")
