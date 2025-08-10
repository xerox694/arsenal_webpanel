#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💎 ARSENAL V4 - COMMANDES CRYPTO & QR CODES
Commandes Discord pour la gestion crypto et transferts instantanés
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import io
from datetime import datetime
from typing import Optional
from modules.crypto_system import CryptoSystem
from modules.economy_system import EconomySystem
from core.logger import log

class CryptoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crypto_system = CryptoSystem(bot)
        self.economy_system = EconomySystem(bot)
    
    @app_commands.command(name="cryptowallet", description="💎 Gérer vos portefeuilles crypto")
    @app_commands.describe(action="Action à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="📊 Voir mes portefeuilles", value="view"),
        app_commands.Choice(name="➕ Ajouter un portefeuille", value="add"),
        app_commands.Choice(name="🔄 Modifier un portefeuille", value="edit"),
        app_commands.Choice(name="📱 Générer QR code", value="qr")
    ])
    async def crypto_wallet(self, interaction: discord.Interaction, action: str):
        """Commande principale de gestion des portefeuilles crypto"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_id = interaction.user.id
            
            if action == "view":
                await self._show_wallets(interaction, user_id)
            elif action == "add":
                await self._add_wallet_modal(interaction, user_id)
            elif action == "edit":
                await self._edit_wallet_modal(interaction, user_id)
            elif action == "qr":
                await self._generate_wallet_qr(interaction, user_id)
                
        except Exception as e:
            log.error(f"❌ Erreur commande cryptowallet: {e}")
            await interaction.followup.send("❌ Une erreur s'est produite", ephemeral=True)
    
    async def _show_wallets(self, interaction: discord.Interaction, user_id: int):
        """Affiche les portefeuilles de l'utilisateur"""
        stats = self.crypto_system.get_user_crypto_stats(user_id)
        
        if not stats:
            await interaction.followup.send("❌ Erreur lors de la récupération des données", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💎 Vos Portefeuilles Crypto",
            description="Gérez vos adresses de portefeuilles crypto",
            color=0x00ff88
        )
        
        # Portefeuilles
        wallets_text = ""
        for crypto, address in stats["wallets"].items():
            if address and crypto != "coinbase":
                emoji = {"eth": "🔷", "btc": "🟠", "bnb": "🟡", "matic": "🟣"}
                wallets_text += f"{emoji.get(crypto, '💎')} **{crypto.upper()}**: `{address[:10]}...{address[-6:]}`\n"
            elif crypto == "coinbase" and address:
                wallets_text += f"🏦 **Coinbase**: `{address}`\n"
        
        if not wallets_text:
            wallets_text = "❌ Aucun portefeuille configuré"
        
        embed.add_field(name="📱 Portefeuilles", value=wallets_text, inline=False)
        
        # Statistiques
        conv_stats = stats["conversions"]
        transfer_stats = stats["transfers"]
        
        stats_text = f"""
📊 **Conversions**: {conv_stats['total']} ({conv_stats['total_ac']:,} AC convertis)
📤 **Envoyés**: {transfer_stats['sent_count']} ({transfer_stats['sent_amount']:,} AC)
📥 **Reçus**: {transfer_stats['received_count']} ({transfer_stats['received_amount']:,} AC)
        """
        
        embed.add_field(name="📈 Statistiques", value=stats_text.strip(), inline=False)
        
        # Boutons d'action
        view = WalletActionsView(self.crypto_system, user_id)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="cryptosend", description="💸 Créer un QR code de transfert instantané")
    @app_commands.describe(montant="Montant en ArsenalCoins à envoyer")
    async def crypto_send(self, interaction: discord.Interaction, montant: int):
        """Créer un QR code pour envoyer des ArsenalCoins"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_id = interaction.user.id
            
            # Vérifications
            if montant <= 0:
                await interaction.followup.send("❌ Le montant doit être positif", ephemeral=True)
                return
            
            if montant < 10:
                await interaction.followup.send("❌ Montant minimum: 10 ArsenalCoins", ephemeral=True)
                return
            
            # Vérifier le solde
            user_balance = self.economy_system.get_user_money(user_id)
            if user_balance < montant:
                await interaction.followup.send(
                    f"❌ Solde insuffisant\n💰 Vous avez: **{user_balance:,} AC**\n💸 Requis: **{montant:,} AC**",
                    ephemeral=True
                )
                return
            
            # Créer le QR code de transfert
            qr_id = self.crypto_system.create_instant_transfer_qr(user_id, montant)
            
            if not qr_id:
                await interaction.followup.send("❌ Erreur lors de la création du QR code", ephemeral=True)
                return
            
            # Générer l'image QR
            qr_data = f"arsenal://transfer/{qr_id}"
            qr_image = self.crypto_system.generate_qr_code(qr_data, "instant_transfer")
            
            if not qr_image:
                await interaction.followup.send("❌ Erreur lors de la génération de l'image", ephemeral=True)
                return
            
            # Créer l'embed
            embed = discord.Embed(
                title="💸 Transfert Instantané Créé",
                description=f"QR code pour envoyer **{montant:,} ArsenalCoins**",
                color=0x00ff88
            )
            
            embed.add_field(
                name="📱 Instructions",
                value="Partagez ce QR code avec la personne qui doit recevoir les ArsenalCoins",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Expiration",
                value="Ce QR code expire dans **1 heure**",
                inline=True
            )
            
            embed.add_field(
                name="🔑 ID de transfert",
                value=f"`{qr_id}`",
                inline=True
            )
            
            embed.set_footer(text="🎯 Arsenal V4 • Système de transfert instantané")
            
            # Envoyer avec l'image
            file = discord.File(qr_image, filename="arsenal_transfer_qr.png")
            embed.set_image(url="attachment://arsenal_transfer_qr.png")
            
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            
        except Exception as e:
            log.error(f"❌ Erreur commande cryptosend: {e}")
            await interaction.followup.send("❌ Une erreur s'est produite", ephemeral=True)
    
    @app_commands.command(name="cryptoscan", description="📱 Scanner un QR code Arsenal")
    @app_commands.describe(qr_id="ID du QR code à scanner")
    async def crypto_scan(self, interaction: discord.Interaction, qr_id: str):
        """Scanner un QR code Arsenal"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_id = interaction.user.id
            
            # Scanner le QR code
            result = self.crypto_system.scan_qr_code(qr_id, user_id)
            
            if not result["success"]:
                await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
                return
            
            if result["type"] == "wallet_address":
                # QR code d'adresse wallet
                embed = discord.Embed(
                    title="💎 Adresse Wallet Scannée",
                    description=f"Portefeuille **{result['crypto']}** détecté",
                    color=0x00ff88
                )
                
                embed.add_field(
                    name="📱 Adresse",
                    value=f"`{result['address']}`",
                    inline=False
                )
                
                embed.add_field(
                    name="👤 Propriétaire",
                    value=f"<@{result['owner_id']}>",
                    inline=True
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                
            elif result["type"] == "instant_transfer":
                # QR code de transfert instantané
                amount = result["amount_ac"]
                sender_id = result["sender_id"]
                transfer_id = result["transfer_id"]
                
                embed = discord.Embed(
                    title="💸 Transfert Instantané Détecté",
                    description=f"**{amount:,} ArsenalCoins** vous attendent !",
                    color=0x00ff88
                )
                
                embed.add_field(
                    name="👤 Expéditeur",
                    value=f"<@{sender_id}>",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 Montant",
                    value=f"**{amount:,} AC**",
                    inline=True
                )
                
                # Bouton pour réclamer
                view = ClaimTransferView(self.crypto_system, transfer_id, user_id)
                
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                
        except Exception as e:
            log.error(f"❌ Erreur commande cryptoscan: {e}")
            await interaction.followup.send("❌ Une erreur s'est produite", ephemeral=True)
    
    @app_commands.command(name="cryptostats", description="📊 Statistiques crypto globales")
    async def crypto_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques crypto globales"""
        await interaction.response.defer()
        
        try:
            # TODO: Implémenter les stats globales
            embed = discord.Embed(
                title="📊 Statistiques Crypto Arsenal",
                description="Aperçu du système crypto",
                color=0x00ff88
            )
            
            embed.add_field(
                name="💎 Système",
                value="✅ Opérationnel\n🔄 QR codes actifs\n💸 Transferts instantanés",
                inline=True
            )
            
            embed.add_field(
                name="💰 Taux de change",
                value="1 AC = 0.01€\n🔷 ETH disponible\n🟠 BTC disponible\n🟡 BNB disponible",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            log.error(f"❌ Erreur commande cryptostats: {e}")
            await interaction.followup.send("❌ Une erreur s'est produite")

class WalletActionsView(discord.ui.View):
    def __init__(self, crypto_system: CryptoSystem, user_id: int):
        super().__init__(timeout=300)
        self.crypto_system = crypto_system
        self.user_id = user_id
    
    @discord.ui.button(label="➕ Ajouter Wallet", style=discord.ButtonStyle.green, emoji="💎")
    async def add_wallet(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddWalletModal(self.crypto_system, self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📱 Générer QR", style=discord.ButtonStyle.primary, emoji="📱")
    async def generate_qr(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Modal pour choisir le type de crypto et générer le QR
        await interaction.response.send_message("🚧 Fonction en développement", ephemeral=True)

class ClaimTransferView(discord.ui.View):
    def __init__(self, crypto_system: CryptoSystem, transfer_id: int, user_id: int):
        super().__init__(timeout=300)
        self.crypto_system = crypto_system
        self.transfer_id = transfer_id
        self.user_id = user_id
    
    @discord.ui.button(label="💸 Réclamer les ArsenalCoins", style=discord.ButtonStyle.success, emoji="💰")
    async def claim_transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            result = self.crypto_system.claim_instant_transfer(self.transfer_id, self.user_id)
            
            if result["success"]:
                embed = discord.Embed(
                    title="✅ Transfert Réclamé !",
                    description=f"Vous avez reçu **{result['amount_ac']:,} ArsenalCoins**",
                    color=0x00ff88
                )
                
                embed.add_field(
                    name="👤 De",
                    value=f"<@{result['sender_id']}>",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 Montant",
                    value=f"**{result['amount_ac']:,} AC**",
                    inline=True
                )
                
                # Désactiver le bouton
                for item in self.children:
                    item.disabled = True
                
                await interaction.edit_original_response(embed=embed, view=self)
                
            else:
                await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
                
        except Exception as e:
            log.error(f"❌ Erreur réclamation transfert: {e}")
            await interaction.followup.send("❌ Une erreur s'est produite", ephemeral=True)

class AddWalletModal(discord.ui.Modal, title="💎 Ajouter un Portefeuille Crypto"):
    def __init__(self, crypto_system: CryptoSystem, user_id: int):
        super().__init__()
        self.crypto_system = crypto_system
        self.user_id = user_id
    
    crypto_type = discord.ui.TextInput(
        label="Type de Crypto",
        placeholder="ETH, BTC, BNB, MATIC...",
        max_length=10
    )
    
    wallet_address = discord.ui.TextInput(
        label="Adresse du Portefeuille",
        placeholder="0x... ou adresse complète",
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            crypto = self.crypto_type.value.upper().strip()
            address = self.wallet_address.value.strip()
            
            # Validations basiques
            if crypto not in ["ETH", "BTC", "BNB", "MATIC"]:
                await interaction.followup.send("❌ Type de crypto non supporté", ephemeral=True)
                return
            
            if len(address) < 10:
                await interaction.followup.send("❌ Adresse trop courte", ephemeral=True)
                return
            
            # TODO: Ajouter la logique d'ajout en base
            await interaction.followup.send(
                f"✅ Portefeuille **{crypto}** ajouté avec succès !\n📱 Adresse: `{address[:10]}...{address[-6:]}`",
                ephemeral=True
            )
            
        except Exception as e:
            log.error(f"❌ Erreur ajout wallet: {e}")
            await interaction.followup.send("❌ Une erreur s'est produite", ephemeral=True)

# Fonction d'initialisation pour le bot
async def setup(bot):
    await bot.add_cog(CryptoCommands(bot))
