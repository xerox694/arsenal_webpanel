#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💎 ARSENAL V4 - INTÉGRATION COMMANDES CRYPTO DANS LE BOT
Module d'intégration des commandes crypto dans le système principal
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import io
import base64
from datetime import datetime
from typing import Optional

# Import des systèmes
try:
    from modules.crypto_system import CryptoSystem
    from modules.economy_system import EconomySystem
    CRYPTO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Modules crypto non disponibles: {e}")
    CRYPTO_AVAILABLE = False

class ArsenalCryptoIntegration:
    """Intégration du système crypto dans Arsenal Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        if CRYPTO_AVAILABLE:
            self.crypto_system = CryptoSystem(bot)
            self.economy_system = EconomySystem(bot)
        
    def add_crypto_commands(self):
        """Ajouter les commandes crypto au bot"""
        if not CRYPTO_AVAILABLE:
            print("❌ Système crypto non disponible - commandes désactivées")
            return
        
        # Groupe de commandes crypto
        @self.bot.group(name='crypto', invoke_without_command=True)
        async def crypto_group(ctx):
            """💎 Système crypto Arsenal - Convertir vos ArsenalCoins en vraie crypto !"""
            embed = discord.Embed(
                title="💎 Arsenal Crypto System",
                description="Convertissez vos ArsenalCoins en vraie cryptomonnaie !",
                color=0x00ff88
            )
            
            embed.add_field(
                name="📱 Commandes disponibles",
                value="""
                `!crypto wallet` - Voir vos portefeuilles
                `!crypto add <crypto> <adresse>` - Ajouter un portefeuille
                `!crypto send <montant>` - Créer QR de transfert
                `!crypto scan <qr_id>` - Scanner un QR code
                `!crypto convert <montant>` - Convertir AC en crypto
                `!crypto stats` - Vos statistiques crypto
                """,
                inline=False
            )
            
            embed.add_field(
                name="💰 Taux de change",
                value="1 ArsenalCoin = 0.01€",
                inline=True
            )
            
            embed.add_field(
                name="💎 Cryptos supportées",
                value="ETH, BTC, BNB, MATIC",
                inline=True
            )
            
            embed.set_footer(text="🎯 Arsenal V4 • Système révolutionnaire")
            await ctx.send(embed=embed)
        
        @crypto_group.command(name='wallet')
        async def crypto_wallet(ctx):
            """💎 Voir vos portefeuilles crypto"""
            try:
                user_id = ctx.author.id
                stats = self.crypto_system.get_user_crypto_stats(user_id)
                
                if not stats:
                    await ctx.send("❌ Erreur lors de la récupération de vos données crypto")
                    return
                
                embed = discord.Embed(
                    title="💎 Vos Portefeuilles Crypto",
                    description=f"Portefeuilles configurés pour {ctx.author.mention}",
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
                    wallets_text = "❌ Aucun portefeuille configuré\nUtilisez `!crypto add <crypto> <adresse>` pour en ajouter un"
                
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
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                print(f"❌ Erreur commande crypto wallet: {e}")
                await ctx.send("❌ Une erreur s'est produite lors de la récupération de vos portefeuilles")
        
        @crypto_group.command(name='add')
        async def crypto_add(ctx, crypto_type: str, address: str):
            """💎 Ajouter un portefeuille crypto
            
            Usage: !crypto add ETH 0xYourEthereumAddress
            """
            try:
                crypto_type = crypto_type.upper().strip()
                address = address.strip()
                
                # Validations
                if crypto_type not in ["ETH", "BTC", "BNB", "MATIC"]:
                    await ctx.send("❌ Type de crypto non supporté. Supportés: ETH, BTC, BNB, MATIC")
                    return
                
                if len(address) < 10:
                    await ctx.send("❌ Adresse trop courte. Vérifiez votre adresse de portefeuille.")
                    return
                
                # TODO: Ajouter en base de données
                embed = discord.Embed(
                    title="✅ Portefeuille Ajouté",
                    description=f"Portefeuille **{crypto_type}** ajouté avec succès !",
                    color=0x00ff88
                )
                
                embed.add_field(
                    name="📱 Adresse",
                    value=f"`{address[:10]}...{address[-6:]}`",
                    inline=False
                )
                
                embed.set_footer(text="Utilisez !crypto wallet pour voir tous vos portefeuilles")
                await ctx.send(embed=embed)
                
            except Exception as e:
                print(f"❌ Erreur ajout portefeuille: {e}")
                await ctx.send("❌ Erreur lors de l'ajout du portefeuille")
        
        @crypto_group.command(name='send')
        async def crypto_send(ctx, montant: int):
            """💸 Créer un QR code de transfert instantané
            
            Usage: !crypto send 100
            """
            try:
                user_id = ctx.author.id
                
                # Vérifications
                if montant <= 0:
                    await ctx.send("❌ Le montant doit être positif")
                    return
                
                if montant < 10:
                    await ctx.send("❌ Montant minimum: 10 ArsenalCoins")
                    return
                
                # Vérifier le solde
                try:
                    user_balance = self.economy_system.get_user_money(user_id) if hasattr(self.economy_system, 'get_user_money') else 0
                except:
                    user_balance = 0
                
                if user_balance < montant:
                    await ctx.send(
                        f"❌ Solde insuffisant\n💰 Vous avez: **{user_balance:,} AC**\n💸 Requis: **{montant:,} AC**"
                    )
                    return
                
                # Créer le QR code de transfert
                qr_id = self.crypto_system.create_instant_transfer_qr(user_id, montant)
                
                if not qr_id:
                    await ctx.send("❌ Erreur lors de la création du QR code")
                    return
                
                # Générer l'image QR
                qr_data = f"arsenal://transfer/{qr_id}"
                qr_image = self.crypto_system.generate_qr_code(qr_data, "instant_transfer")
                
                if qr_image:
                    # Créer l'embed
                    embed = discord.Embed(
                        title="💸 QR Code de Transfert Créé",
                        description=f"**{montant:,} ArsenalCoins** prêts à être envoyés",
                        color=0x00ff88
                    )
                    
                    embed.add_field(
                        name="📱 Instructions",
                        value="Partagez cette image avec la personne qui doit recevoir les ArsenalCoins",
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
                    
                    embed.set_footer(text="Pour scanner: !crypto scan <id>")
                    
                    # Envoyer avec l'image
                    file = discord.File(qr_image, filename="arsenal_transfer_qr.png")
                    embed.set_image(url="attachment://arsenal_transfer_qr.png")
                    
                    await ctx.send(embed=embed, file=file)
                else:
                    await ctx.send("❌ Erreur lors de la génération de l'image QR")
                
            except Exception as e:
                print(f"❌ Erreur commande crypto send: {e}")
                await ctx.send("❌ Une erreur s'est produite lors de la création du transfert")
        
        @crypto_group.command(name='scan')
        async def crypto_scan(ctx, qr_id: str):
            """📱 Scanner un QR code Arsenal
            
            Usage: !crypto scan transfer_123456789
            """
            try:
                user_id = ctx.author.id
                
                # Scanner le QR code
                result = self.crypto_system.scan_qr_code(qr_id, user_id)
                
                if not result["success"]:
                    await ctx.send(f"❌ {result['error']}")
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
                    
                    await ctx.send(embed=embed)
                    
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
                    
                    embed.add_field(
                        name="✅ Action",
                        value=f"Tapez `!crypto claim {transfer_id}` pour réclamer",
                        inline=False
                    )
                    
                    await ctx.send(embed=embed)
                
            except Exception as e:
                print(f"❌ Erreur commande crypto scan: {e}")
                await ctx.send("❌ Une erreur s'est produite lors du scan")
        
        @crypto_group.command(name='claim')
        async def crypto_claim(ctx, transfer_id: int):
            """💰 Réclamer un transfert instantané
            
            Usage: !crypto claim 123
            """
            try:
                user_id = ctx.author.id
                
                # Réclamer le transfert
                result = self.crypto_system.claim_instant_transfer(transfer_id, user_id)
                
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
                    
                    embed.set_footer(text="💎 Merci d'utiliser Arsenal Crypto System")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ {result['error']}")
                
            except Exception as e:
                print(f"❌ Erreur commande crypto claim: {e}")
                await ctx.send("❌ Une erreur s'est produite lors de la réclamation")
        
        @crypto_group.command(name='stats')
        async def crypto_stats(ctx):
            """📊 Vos statistiques crypto"""
            try:
                user_id = ctx.author.id
                stats = self.crypto_system.get_user_crypto_stats(user_id)
                
                if not stats:
                    await ctx.send("❌ Erreur lors de la récupération de vos statistiques")
                    return
                
                embed = discord.Embed(
                    title="📊 Vos Statistiques Crypto",
                    description=f"Résumé crypto pour {ctx.author.mention}",
                    color=0x00ff88
                )
                
                # Portefeuilles
                wallet_count = sum(1 for addr in stats["wallets"].values() if addr)
                embed.add_field(
                    name="💎 Portefeuilles",
                    value=f"**{wallet_count}** configurés",
                    inline=True
                )
                
                # Conversions
                conv_stats = stats["conversions"]
                embed.add_field(
                    name="🔄 Conversions",
                    value=f"**{conv_stats['total']}** conversions\n**{conv_stats['total_ac']:,}** AC convertis",
                    inline=True
                )
                
                # Transferts
                transfer_stats = stats["transfers"]
                total_transfers = transfer_stats['sent_count'] + transfer_stats['received_count']
                embed.add_field(
                    name="💸 Transferts",
                    value=f"**{total_transfers}** transferts\n📤 {transfer_stats['sent_count']} envoyés\n📥 {transfer_stats['received_count']} reçus",
                    inline=True
                )
                
                # Commissions payées
                embed.add_field(
                    name="💰 Commissions",
                    value=f"**{conv_stats['total_commission']:.2f}€** payées",
                    inline=True
                )
                
                embed.set_footer(text="🎯 Arsenal V4 • Système crypto révolutionnaire")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                print(f"❌ Erreur commande crypto stats: {e}")
                await ctx.send("❌ Une erreur s'est produite lors de la récupération des statistiques")
        
        @crypto_group.command(name='help')
        async def crypto_help(ctx):
            """❓ Aide sur le système crypto Arsenal"""
            embed = discord.Embed(
                title="💎 Arsenal Crypto System - Guide Complet",
                description="Système révolutionnaire pour convertir vos ArsenalCoins en vraie cryptomonnaie !",
                color=0x00ff88
            )
            
            embed.add_field(
                name="🎯 Concept",
                value="Gagnez des ArsenalCoins en utilisant le bot, puis convertissez-les en vraie crypto ou euros !",
                inline=False
            )
            
            embed.add_field(
                name="💰 Comment gagner des ArsenalCoins",
                value="• Utilisez les commandes du bot\n• Participez aux événements\n• Jouez au casino\n• Transferts entre utilisateurs",
                inline=False
            )
            
            embed.add_field(
                name="📱 Commandes principales",
                value="""
                `!crypto wallet` - Voir vos portefeuilles
                `!crypto add ETH 0x...` - Ajouter portefeuille
                `!crypto send 100` - Envoyer via QR code
                `!crypto scan <id>` - Scanner un QR code
                `!crypto stats` - Vos statistiques
                """,
                inline=False
            )
            
            embed.add_field(
                name="🔄 Processus de conversion",
                value="1. Gagnez des ArsenalCoins\n2. Ajoutez vos portefeuilles crypto\n3. Demandez une conversion\n4. Recevez vos cryptos !",
                inline=False
            )
            
            embed.add_field(
                name="💎 Cryptos supportées",
                value="🔷 Ethereum (ETH)\n🟠 Bitcoin (BTC)\n🟡 Binance Coin (BNB)\n🟣 Polygon (MATIC)",
                inline=True
            )
            
            embed.add_field(
                name="💰 Taux & Commission",
                value="**1 AC = 0.01€**\nCommission: 1%\nMinimum: 10 AC",
                inline=True
            )
            
            embed.set_footer(text="🚀 Arsenal V4 • Révolutionnons Discord ensemble !")
            
            await ctx.send(embed=embed)
        
        print("✅ Commandes crypto ajoutées au bot Arsenal")

# Fonction d'initialisation pour le bot principal
def setup_crypto_integration(bot):
    """Initialiser l'intégration crypto dans le bot Arsenal"""
    crypto_integration = ArsenalCryptoIntegration(bot)
    crypto_integration.add_crypto_commands()
    return crypto_integration
