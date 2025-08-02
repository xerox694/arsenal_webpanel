#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎧 ARSENAL V4 - PANNEAU DE CONTRÔLE VOCAL INTÉGRÉ
Panel avec boutons interactifs dans le chat textuel de la vocale temporaire
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

class VoiceControlView(discord.ui.View):
    """Panel de contrôle interactif pour les vocales temporaires"""
    
    def __init__(self, voice_channel: discord.VoiceChannel, text_channel: discord.abc.GuildChannel, owner: discord.Member):
        super().__init__(timeout=None)
        self.voice_channel = voice_channel
        self.text_channel = text_channel  # Peut être une VoiceChannel ou TextChannel
        self.owner = owner
        self.custom_id = f"voice_control_{voice_channel.id}"
        
        # Données du salon (whitelist, blacklist, etc.)
        self.channel_data = {
            "whitelist": [],
            "blacklist": [],
            "temp_roles": [],
            "is_locked": False,
            "is_hidden": False,
            "user_limit": 0
        }
    
    def is_owner_or_mod(self, user: discord.Member) -> bool:
        """Vérifie si l'utilisateur peut utiliser les contrôles"""
        return (user.id == self.owner.id or 
                user.guild_permissions.administrator or
                user.guild_permissions.manage_channels)
    
    @discord.ui.button(label="🔒 Verrouiller", style=discord.ButtonStyle.gray, row=0)
    async def lock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        if self.channel_data["is_locked"]:
            # Déverrouiller
            await self.voice_channel.set_permissions(interaction.guild.default_role, connect=True)
            self.channel_data["is_locked"] = False
            button.label = "🔒 Verrouiller"
            button.style = discord.ButtonStyle.gray
            await interaction.response.send_message("🔓 Salon déverrouillé", ephemeral=True)
        else:
            # Verrouiller
            await self.voice_channel.set_permissions(interaction.guild.default_role, connect=False)
            # Autoriser les membres déjà présents et la whitelist
            for member in self.voice_channel.members:
                await self.voice_channel.set_permissions(member, connect=True)
            for user_id in self.channel_data["whitelist"]:
                member = interaction.guild.get_member(user_id)
                if member:
                    await self.voice_channel.set_permissions(member, connect=True)
            
            self.channel_data["is_locked"] = True
            button.label = "🔓 Déverrouiller"
            button.style = discord.ButtonStyle.red
            await interaction.response.send_message("🔒 Salon verrouillé", ephemeral=True)
        
        await interaction.edit_original_response(view=self)
    
    @discord.ui.button(label="👁️ Masquer", style=discord.ButtonStyle.gray, row=0)
    async def hide_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        if self.channel_data["is_hidden"]:
            # Rendre visible
            await self.voice_channel.set_permissions(interaction.guild.default_role, view_channel=True)
            self.channel_data["is_hidden"] = False
            button.label = "👁️ Masquer"
            button.style = discord.ButtonStyle.gray
            await interaction.response.send_message("👁️ Salon rendu visible", ephemeral=True)
        else:
            # Masquer
            await self.voice_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            # Autoriser les membres présents et la whitelist à voir
            for member in self.voice_channel.members:
                await self.voice_channel.set_permissions(member, view_channel=True)
            for user_id in self.channel_data["whitelist"]:
                member = interaction.guild.get_member(user_id)
                if member:
                    await self.voice_channel.set_permissions(member, view_channel=True)
            
            self.channel_data["is_hidden"] = True
            button.label = "👁️‍🗨️ Montrer"
            button.style = discord.ButtonStyle.green
            await interaction.response.send_message("🫥 Salon masqué", ephemeral=True)
        
        await interaction.edit_original_response(view=self)
    
    @discord.ui.button(label="👥 Limite", style=discord.ButtonStyle.gray, row=0)
    async def set_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        modal = UserLimitModal(self.voice_channel, self.channel_data)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✏️ Renommer", style=discord.ButtonStyle.gray, row=0)
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        modal = RenameChannelModal(self.voice_channel, self.text_channel)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔄 Transférer", style=discord.ButtonStyle.gray, row=0)
    async def transfer_ownership(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message("❌ Seul le propriétaire actuel peut transférer la propriété", ephemeral=True)
            return
        
        modal = TransferOwnershipModal(self, self.text_channel)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="➕ Whitelist", style=discord.ButtonStyle.green, row=1)
    async def manage_whitelist(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        modal = WhitelistModal(self.voice_channel, self.channel_data, "whitelist")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="➖ Blacklist", style=discord.ButtonStyle.red, row=1)
    async def manage_blacklist(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        modal = BlacklistModal(self.voice_channel, self.channel_data, "blacklist")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎭 Rôle Temp", style=discord.ButtonStyle.blurple, row=1)
    async def create_temp_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        modal = TempRoleModal(interaction.guild, self.channel_data, self.voice_channel)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👢 Expulser", style=discord.ButtonStyle.red, row=1)
    async def kick_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        if len(self.voice_channel.members) <= 1:
            await interaction.response.send_message("❌ Aucun membre à expulser", ephemeral=True)
            return
        
        view = KickUserView(self.voice_channel, interaction.user)
        embed = discord.Embed(
            title="👢 Expulser un Utilisateur",
            description="Sélectionnez l'utilisateur à expulser du salon vocal",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger, row=1)
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_owner_or_mod(interaction.user):
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce bouton", ephemeral=True)
            return
        
        view = ConfirmDeleteView(self.voice_channel, self.text_channel, self.channel_data)
        embed = discord.Embed(
            title="⚠️ Confirmer la Suppression",
            description=f"Êtes-vous sûr de vouloir supprimer **{self.voice_channel.name}** ?\n\nCette action est **irréversible** !",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class UserLimitModal(discord.ui.Modal):
    def __init__(self, voice_channel: discord.VoiceChannel, channel_data: dict):
        super().__init__(title="👥 Définir la Limite d'Utilisateurs")
        self.voice_channel = voice_channel
        self.channel_data = channel_data
        
    limit_input = discord.ui.TextInput(
        label="Limite d'utilisateurs (0 = pas de limite)",
        placeholder="Entrez un nombre entre 0 et 99",
        min_length=1,
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.limit_input.value)
            if limit < 0 or limit > 99:
                await interaction.response.send_message("❌ La limite doit être entre 0 et 99", ephemeral=True)
                return
            
            await self.voice_channel.edit(user_limit=limit)
            self.channel_data["user_limit"] = limit
            
            if limit == 0:
                await interaction.response.send_message("✅ Limite supprimée (illimité)", ephemeral=True)
            else:
                await interaction.response.send_message(f"✅ Limite définie à {limit} utilisateur(s)", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un nombre valide", ephemeral=True)

class RenameChannelModal(discord.ui.Modal):
    def __init__(self, voice_channel: discord.VoiceChannel, text_channel: discord.abc.GuildChannel):
        super().__init__(title="✏️ Renommer le Salon")
        self.voice_channel = voice_channel
        self.text_channel = text_channel
        
    name_input = discord.ui.TextInput(
        label="Nouveau nom du salon",
        placeholder="Entrez le nouveau nom...",
        min_length=1,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_name = self.name_input.value.strip()
            old_name = self.voice_channel.name
            
            # Renommer seulement la vocale (pas de chat textuel séparé maintenant)
            await self.voice_channel.edit(name=f"🎧 {new_name}")
            
            embed = discord.Embed(
                title="✅ Salon Renommé",
                description=f"**Ancien nom:** {old_name}\n**Nouveau nom:** 🎧 {new_name}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du renommage: {str(e)}", ephemeral=True)

class TransferOwnershipModal(discord.ui.Modal):
    def __init__(self, control_view: VoiceControlView, text_channel: discord.abc.GuildChannel):
        super().__init__(title="🔄 Transférer la Propriété")
        self.control_view = control_view
        self.text_channel = text_channel
        
    user_input = discord.ui.TextInput(
        label="Nouvel propriétaire (mention ou ID)",
        placeholder="@utilisateur ou ID utilisateur",
        min_length=1,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_input = self.user_input.value.strip()
            
            # Essayer de parser l'utilisateur
            new_owner = None
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
                new_owner = interaction.guild.get_member(user_id)
            else:
                try:
                    user_id = int(user_input)
                    new_owner = interaction.guild.get_member(user_id)
                except ValueError:
                    pass
            
            if not new_owner:
                await interaction.response.send_message("❌ Utilisateur introuvable", ephemeral=True)
                return
            
            if new_owner.bot:
                await interaction.response.send_message("❌ Impossible de transférer à un bot", ephemeral=True)
                return
            
            if new_owner.id == self.control_view.owner.id:
                await interaction.response.send_message("❌ Vous êtes déjà propriétaire", ephemeral=True)
                return
            
            # Transférer la propriété
            old_owner = self.control_view.owner
            self.control_view.owner = new_owner
            
            # Mettre à jour les permissions
            await self.control_view.voice_channel.set_permissions(old_owner, overwrite=None)
            await self.control_view.voice_channel.set_permissions(new_owner, manage_permissions=True, move_members=True)
            await self.text_channel.set_permissions(new_owner, manage_messages=True, manage_channels=True)
            
            embed = discord.Embed(
                title="🔄 Propriété Transférée",
                description=f"**Ancien propriétaire:** {old_owner.mention}\n**Nouveau propriétaire:** {new_owner.mention}",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
            
            # Notifier le nouveau propriétaire
            await self.text_channel.send(f"🎉 {new_owner.mention}, vous êtes maintenant propriétaire de ce salon !")
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du transfert: {str(e)}", ephemeral=True)

class WhitelistModal(discord.ui.Modal):
    def __init__(self, voice_channel: discord.VoiceChannel, channel_data: dict, list_type: str):
        super().__init__(title="➕ Gérer la Whitelist")
        self.voice_channel = voice_channel
        self.channel_data = channel_data
        self.list_type = list_type
        
    action_input = discord.ui.TextInput(
        label="Action (add/remove/list)",
        placeholder="add, remove ou list",
        min_length=3,
        max_length=6
    )
    
    user_input = discord.ui.TextInput(
        label="Utilisateur (pour add/remove)",
        placeholder="@utilisateur ou ID utilisateur",
        required=False,
        min_length=0,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        action = self.action_input.value.lower().strip()
        
        if action == "list":
            whitelist_users = []
            for user_id in self.channel_data["whitelist"]:
                user = interaction.guild.get_member(user_id)
                if user:
                    whitelist_users.append(user.display_name)
            
            if whitelist_users:
                embed = discord.Embed(
                    title="📋 Whitelist Actuelle",
                    description="\n".join([f"• {name}" for name in whitelist_users]),
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="📋 Whitelist Vide",
                    description="Aucun utilisateur dans la whitelist",
                    color=discord.Color.gray()
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.user_input.value:
            await interaction.response.send_message("❌ Veuillez spécifier un utilisateur", ephemeral=True)
            return
        
        # Parser l'utilisateur
        user_input = self.user_input.value.strip()
        target_user = None
        
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = int(user_input[2:-1].replace('!', ''))
            target_user = interaction.guild.get_member(user_id)
        else:
            try:
                user_id = int(user_input)
                target_user = interaction.guild.get_member(user_id)
            except ValueError:
                pass
        
        if not target_user:
            await interaction.response.send_message("❌ Utilisateur introuvable", ephemeral=True)
            return
        
        if action == "add":
            if target_user.id not in self.channel_data["whitelist"]:
                self.channel_data["whitelist"].append(target_user.id)
                # Donner les permissions si le salon est verrouillé/masqué
                if self.channel_data.get("is_locked"):
                    await self.voice_channel.set_permissions(target_user, connect=True)
                if self.channel_data.get("is_hidden"):
                    await self.voice_channel.set_permissions(target_user, view_channel=True)
                
                await interaction.response.send_message(f"✅ {target_user.display_name} ajouté à la whitelist", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {target_user.display_name} est déjà dans la whitelist", ephemeral=True)
        
        elif action == "remove":
            if target_user.id in self.channel_data["whitelist"]:
                self.channel_data["whitelist"].remove(target_user.id)
                # Retirer les permissions personnalisées
                await self.voice_channel.set_permissions(target_user, overwrite=None)
                await interaction.response.send_message(f"✅ {target_user.display_name} retiré de la whitelist", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {target_user.display_name} n'est pas dans la whitelist", ephemeral=True)
        
        else:
            await interaction.response.send_message("❌ Action non reconnue. Utilisez: add, remove ou list", ephemeral=True)

class BlacklistModal(discord.ui.Modal):
    def __init__(self, voice_channel: discord.VoiceChannel, channel_data: dict, list_type: str):
        super().__init__(title="➖ Gérer la Blacklist")
        self.voice_channel = voice_channel
        self.channel_data = channel_data
        self.list_type = list_type
        
    action_input = discord.ui.TextInput(
        label="Action (add/remove/list)",
        placeholder="add, remove ou list",
        min_length=3,
        max_length=6
    )
    
    user_input = discord.ui.TextInput(
        label="Utilisateur (pour add/remove)",
        placeholder="@utilisateur ou ID utilisateur",
        required=False,
        min_length=0,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        action = self.action_input.value.lower().strip()
        
        if action == "list":
            blacklist_users = []
            for user_id in self.channel_data["blacklist"]:
                user = interaction.guild.get_member(user_id)
                if user:
                    blacklist_users.append(user.display_name)
            
            if blacklist_users:
                embed = discord.Embed(
                    title="🚫 Blacklist Actuelle",
                    description="\n".join([f"• {name}" for name in blacklist_users]),
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="🚫 Blacklist Vide",
                    description="Aucun utilisateur dans la blacklist",
                    color=discord.Color.gray()
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.user_input.value:
            await interaction.response.send_message("❌ Veuillez spécifier un utilisateur", ephemeral=True)
            return
        
        # Parser l'utilisateur (même logique que whitelist)
        user_input = self.user_input.value.strip()
        target_user = None
        
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = int(user_input[2:-1].replace('!', ''))
            target_user = interaction.guild.get_member(user_id)
        else:
            try:
                user_id = int(user_input)
                target_user = interaction.guild.get_member(user_id)
            except ValueError:
                pass
        
        if not target_user:
            await interaction.response.send_message("❌ Utilisateur introuvable", ephemeral=True)
            return
        
        if action == "add":
            if target_user.id not in self.channel_data["blacklist"]:
                self.channel_data["blacklist"].append(target_user.id)
                # Interdire l'accès
                await self.voice_channel.set_permissions(target_user, connect=False, view_channel=False)
                # Expulser s'il est présent
                if target_user in self.voice_channel.members:
                    await target_user.move_to(None)
                
                await interaction.response.send_message(f"✅ {target_user.display_name} ajouté à la blacklist", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {target_user.display_name} est déjà dans la blacklist", ephemeral=True)
        
        elif action == "remove":
            if target_user.id in self.channel_data["blacklist"]:
                self.channel_data["blacklist"].remove(target_user.id)
                # Rétablir les permissions par défaut
                await self.voice_channel.set_permissions(target_user, overwrite=None)
                await interaction.response.send_message(f"✅ {target_user.display_name} retiré de la blacklist", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {target_user.display_name} n'est pas dans la blacklist", ephemeral=True)
        
        else:
            await interaction.response.send_message("❌ Action non reconnue. Utilisez: add, remove ou list", ephemeral=True)

class TempRoleModal(discord.ui.Modal):
    def __init__(self, guild: discord.Guild, channel_data: dict, voice_channel: discord.VoiceChannel):
        super().__init__(title="🎭 Créer un Rôle Temporaire")
        self.guild = guild
        self.channel_data = channel_data
        self.voice_channel = voice_channel
        
    role_name = discord.ui.TextInput(
        label="Nom du rôle",
        placeholder="Ex: VIP Vocal, Membre Premium...",
        min_length=1,
        max_length=100
    )
    
    role_color = discord.ui.TextInput(
        label="Couleur (hex, ex: #ff0000)",
        placeholder="#ff0000 pour rouge, #00ff00 pour vert...",
        required=False,
        min_length=0,
        max_length=7
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parser la couleur
            color = discord.Color.default()
            if self.role_color.value:
                hex_color = self.role_color.value.strip()
                if hex_color.startswith('#'):
                    hex_color = hex_color[1:]
                color = discord.Color(int(hex_color, 16))
            
            # Créer le rôle temporaire
            temp_role = await self.guild.create_role(
                name=self.role_name.value.strip(),
                color=color,
                reason=f"Rôle temporaire pour {self.voice_channel.name}"
            )
            
            # L'ajouter à la liste des rôles temporaires
            self.channel_data["temp_roles"].append(temp_role.id)
            
            embed = discord.Embed(
                title="🎭 Rôle Temporaire Créé",
                description=f"**Rôle:** {temp_role.mention}\n**Couleur:** {temp_role.color}\n\n*Ce rôle sera supprimé à la fermeture du salon*",
                color=temp_role.color
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Couleur invalide. Utilisez le format #ff0000", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la création du rôle: {str(e)}", ephemeral=True)

class KickUserView(discord.ui.View):
    def __init__(self, voice_channel: discord.VoiceChannel, kicker: discord.Member):
        super().__init__(timeout=60)
        self.voice_channel = voice_channel
        self.kicker = kicker
        
        # Ajouter un select menu avec les membres présents
        options = []
        for member in voice_channel.members:
            if member != kicker:  # Ne pas inclure celui qui expulse
                options.append(discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id),
                    description=f"ID: {member.id}"
                ))
        
        if options:
            self.add_item(KickUserSelect(voice_channel, options))
    
class KickUserSelect(discord.ui.Select):
    def __init__(self, voice_channel: discord.VoiceChannel, options: List[discord.SelectOption]):
        super().__init__(placeholder="Sélectionnez un utilisateur à expulser", options=options)
        self.voice_channel = voice_channel
        
    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        member = interaction.guild.get_member(user_id)
        
        if member and member in self.voice_channel.members:
            await member.move_to(None)
            await interaction.response.send_message(f"👢 {member.display_name} a été expulsé du salon", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Utilisateur introuvable ou plus dans le salon", ephemeral=True)

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, voice_channel: discord.VoiceChannel, text_channel: discord.abc.GuildChannel, channel_data: dict):
        super().__init__(timeout=30)
        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.channel_data = channel_data
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Supprimer les rôles temporaires
            for role_id in self.channel_data.get("temp_roles", []):
                role = interaction.guild.get_role(role_id)
                if role:
                    await role.delete(reason="Suppression salon temporaire")
            
            # Supprimer les salons
            await self.text_channel.delete(reason="Suppression salon temporaire")
            await self.voice_channel.delete(reason="Suppression salon temporaire")
            
            await interaction.response.send_message("✅ Salon supprimé avec succès", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la suppression: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.gray)
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Suppression annulée", ephemeral=True)
        self.stop()

async def setup(bot):
    """Setup du module de contrôle vocal"""
    log.info("🎧 Module Voice Control Panel chargé")
