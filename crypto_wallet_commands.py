"""
💳 Arsenal V4 - Commandes Crypto Wallet
Commandes Discord pour gérer les wallets crypto
"""

import discord
from discord.ext import commands
import asyncio
import json
import os
from crypto_wallet_system import crypto_wallet
from economy_system import economy_db

class CryptoWalletCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crypto_wallet = crypto_wallet

    @commands.command(name='wallet', aliases=['mywallet', 'portefeuille'])
    async def wallet_info(self, ctx):
        """💳 Afficher mes informations de wallet crypto"""
        try:
            user_id = str(ctx.author.id)
            
            # Récupérer le solde ArsenalCoins
            user_wallet = economy_db.get_user_wallet(user_id, ctx.author.name)
            arsenal_balance = user_wallet[2] if user_wallet else 0
            
            # Récupérer les wallets crypto
            crypto_wallets = self.crypto_wallet.get_user_wallets(user_id)
            
            # Calculer la valeur en euros
            euro_value = arsenal_balance * 0.01
            
            embed = discord.Embed(
                title="💳 Mon Wallet Arsenal",
                description=f"Informations pour {ctx.author.mention}",
                color=0x00d4ff
            )
            
            # Section ArsenalCoins
            embed.add_field(
                name="🪙 ArsenalCoins",
                value=f"**{arsenal_balance:,}** AC\n≈ **{euro_value:.2f} €**",
                inline=True
            )
            
            # Section Taux de conversion
            embed.add_field(
                name="📊 Taux de conversion",
                value="1 ArsenalCoin = 0.01 €\nCommission: 1%",
                inline=True
            )
            
            # Section Wallets crypto
            if crypto_wallets:
                wallet_list = []
                for wallet in crypto_wallets[:3]:  # Limiter à 3 wallets
                    verified = "✅" if wallet['verified'] else "⏳"
                    nickname = wallet['nickname'] or f"Wallet {wallet['type']}"
                    address = wallet['address'][:10] + "..." if len(wallet['address']) > 10 else wallet['address']
                    wallet_list.append(f"{verified} **{nickname}**\n`{address}`")
                
                embed.add_field(
                    name=f"🏦 Mes Wallets Crypto ({len(crypto_wallets)})",
                    value="\n\n".join(wallet_list) if wallet_list else "Aucun wallet enregistré",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🏦 Mes Wallets Crypto",
                    value="Aucun wallet enregistré\nUtilisez `/addwallet` pour en ajouter un",
                    inline=False
                )
            
            # Instructions
            embed.add_field(
                name="🚀 Actions disponibles",
                value=(
                    "`/addwallet` - Ajouter un wallet crypto\n"
                    "`/convert` - Convertir ArsenalCoins\n"
                    "`/history` - Voir l'historique"
                ),
                inline=False
            )
            
            embed.set_footer(text="Arsenal Crypto Wallet System | Taux: 1 AC = 0.01 €")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/123/456/wallet_icon.png")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Erreur commande wallet: {e}")
            await ctx.send("❌ Erreur lors de la récupération des informations du wallet.")

    @commands.command(name='addwallet', aliases=['addcrypto'])
    async def add_wallet(self, ctx, wallet_type: str = None, *, wallet_address: str = None):
        """💳 Ajouter un wallet crypto"""
        try:
            if not wallet_type or not wallet_address:
                embed = discord.Embed(
                    title="💳 Ajouter un Wallet Crypto",
                    description="Format: `/addwallet <type> <adresse> [surnom]`",
                    color=0x00d4ff
                )
                embed.add_field(
                    name="Types supportés",
                    value="• `ETH` - Ethereum\n• `BTC` - Bitcoin\n• `BNB` - Binance Smart Chain\n• `MATIC` - Polygon",
                    inline=True
                )
                embed.add_field(
                    name="Exemple",
                    value="`/addwallet ETH 0x1234567890abcdef... Mon wallet principal`",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            # Valider le type de wallet
            valid_types = ['ETH', 'BTC', 'BNB', 'MATIC']
            wallet_type = wallet_type.upper()
            
            if wallet_type not in valid_types:
                await ctx.send(f"❌ Type de wallet invalide. Types supportés: {', '.join(valid_types)}")
                return
            
            # Extraire le surnom si présent
            parts = wallet_address.split(' ', 1)
            address = parts[0]
            nickname = parts[1] if len(parts) > 1 else None
            
            # Ajouter le wallet
            result = self.crypto_wallet.add_crypto_wallet(
                user_id=str(ctx.author.id),
                wallet_address=address,
                wallet_type=wallet_type,
                nickname=nickname
            )
            
            if result['success']:
                embed = discord.Embed(
                    title="✅ Wallet ajouté avec succès",
                    description=f"Wallet {wallet_type} enregistré pour {ctx.author.mention}",
                    color=0x00ff88
                )
                embed.add_field(
                    name="Type", 
                    value=wallet_type, 
                    inline=True
                )
                embed.add_field(
                    name="Adresse", 
                    value=f"`{address[:20]}...`", 
                    inline=True
                )
                if nickname:
                    embed.add_field(
                        name="Surnom", 
                        value=nickname, 
                        inline=True
                    )
                
                embed.set_footer(text="Utilisez /wallet pour voir tous vos wallets")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ {result['error']}")
                
        except Exception as e:
            print(f"❌ Erreur commande addwallet: {e}")
            await ctx.send("❌ Erreur lors de l'ajout du wallet.")

    @commands.command(name='convert', aliases=['convertir'])
    async def convert_coins(self, ctx, amount: int = None):
        """💱 Convertir ArsenalCoins en crypto/fiat"""
        try:
            if not amount:
                embed = discord.Embed(
                    title="💱 Convertir ArsenalCoins",
                    description="Format: `/convert <montant>`",
                    color=0x00d4ff
                )
                embed.add_field(
                    name="Exemple",
                    value="`/convert 100` - Convertir 100 ArsenalCoins",
                    inline=True
                )
                embed.add_field(
                    name="Taux",
                    value="1 ArsenalCoin = 0.01 €\nCommission: 1%",
                    inline=True
                )
                await ctx.send(embed=embed)
                return
            
            if amount < 1:
                await ctx.send("❌ Montant minimum: 1 ArsenalCoin")
                return
            
            user_id = str(ctx.author.id)
            
            # Vérifier le solde
            user_wallet = economy_db.get_user_wallet(user_id, ctx.author.name)
            current_balance = user_wallet[2] if user_wallet else 0
            
            if current_balance < amount:
                await ctx.send(f"❌ Solde insuffisant. Vous avez {current_balance} ArsenalCoins.")
                return
            
            # Calculer la conversion
            calculation = self.crypto_wallet.calculate_conversion(amount)
            
            if not calculation:
                await ctx.send("❌ Erreur de calcul de conversion.")
                return
            
            # Afficher l'aperçu
            embed = discord.Embed(
                title="💱 Aperçu de la conversion",
                description=f"Conversion pour {ctx.author.mention}",
                color=0xffd700
            )
            
            embed.add_field(
                name="ArsenalCoins",
                value=f"**{calculation['arsenal_coins']:,}** 🪙",
                inline=True
            )
            embed.add_field(
                name="Valeur brute",
                value=f"**{calculation['euro_value']:.2f} €**",
                inline=True
            )
            embed.add_field(
                name="Commission (1%)",
                value=f"**-{calculation['commission']:.2f} €**",
                inline=True
            )
            embed.add_field(
                name="💰 Montant final",
                value=f"**{calculation['final_amount']:.2f} €**",
                inline=False
            )
            
            embed.set_footer(text="Réagissez avec ✅ pour confirmer la conversion")
            
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            
            # Attendre la réaction
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                
                if str(reaction.emoji) == "✅":
                    # Confirmer la conversion
                    result = self.crypto_wallet.request_conversion(
                        user_id=user_id,
                        arsenal_coins_amount=amount
                    )
                    
                    if result['success']:
                        embed = discord.Embed(
                            title="✅ Conversion demandée",
                            description=f"Transaction: `{result['transaction_id']}`",
                            color=0x00ff88
                        )
                        embed.add_field(
                            name="Montant final",
                            value=f"**{result['conversion']['final_amount']:.2f} €**",
                            inline=True
                        )
                        embed.add_field(
                            name="Status",
                            value="🟡 En attente de traitement",
                            inline=True
                        )
                        embed.set_footer(text="La conversion sera traitée sous 24h")
                        
                        await message.edit(embed=embed)
                    else:
                        await message.edit(content=f"❌ {result['error']}")
                else:
                    await message.edit(content="❌ Conversion annulée.")
                    
            except asyncio.TimeoutError:
                await message.edit(content="⏰ Conversion expirée (30s).")
                
        except Exception as e:
            print(f"❌ Erreur commande convert: {e}")
            await ctx.send("❌ Erreur lors de la conversion.")

    @commands.command(name='cryptohistory', aliases=['history', 'historique'])
    async def conversion_history(self, ctx):
        """📊 Historique des conversions crypto"""
        try:
            user_id = str(ctx.author.id)
            history = self.crypto_wallet.get_conversion_history(user_id, limit=10)
            
            if not history:
                embed = discord.Embed(
                    title="📊 Historique des conversions",
                    description="Aucune conversion effectuée",
                    color=0x00d4ff
                )
                embed.set_footer(text="Utilisez /convert pour effectuer votre première conversion")
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📊 Historique des conversions",
                description=f"Dernières conversions de {ctx.author.mention}",
                color=0x00d4ff
            )
            
            for conv in history[:5]:  # Limiter à 5 pour Discord
                status_emoji = {
                    'PENDING': '🟡',
                    'COMPLETED': '✅',
                    'FAILED': '❌'
                }.get(conv['status'], '❓')
                
                date = conv['created_at'][:10] if conv['created_at'] else 'N/A'
                
                embed.add_field(
                    name=f"{status_emoji} {conv['transaction_id']}",
                    value=(
                        f"**{conv['arsenal_coins']} AC** → **{conv['final_amount']:.2f} €**\n"
                        f"Commission: {conv['commission']:.2f} €\n"
                        f"Date: {date}"
                    ),
                    inline=True
                )
            
            if len(history) > 5:
                embed.set_footer(text=f"Et {len(history) - 5} autres conversions... Voir plus sur le webpanel")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Erreur commande history: {e}")
            await ctx.send("❌ Erreur lors de la récupération de l'historique.")

    @commands.command(name='cryptostats', aliases=['stats'])
    @commands.has_permissions(administrator=True)
    async def crypto_stats(self, ctx):
        """📈 Statistiques globales crypto (Admin seulement)"""
        try:
            stats = self.crypto_wallet.get_commission_stats()
            
            embed = discord.Embed(
                title="📈 Statistiques Crypto Wallet",
                description="Statistiques globales du système",
                color=0xffd700
            )
            
            embed.add_field(
                name="💰 Total commissions",
                value=f"**{stats['total_commissions']:.2f} €**",
                inline=True
            )
            embed.add_field(
                name="📅 Commissions aujourd'hui",
                value=f"**{stats['today_commissions']:.2f} €**",
                inline=True
            )
            embed.add_field(
                name="🔄 Total conversions",
                value=f"**{stats['total_conversions']}**",
                inline=True
            )
            embed.add_field(
                name="📊 Taux de commission",
                value=f"**{stats['commission_rate']}%**",
                inline=True
            )
            
            embed.set_footer(text="Arsenal Crypto Wallet System - Admin Stats")
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"❌ Erreur commande cryptostats: {e}")
            await ctx.send("❌ Erreur lors de la récupération des statistiques.")

# Fonction pour ajouter le cog au bot
async def setup(bot):
    await bot.add_cog(CryptoWalletCommands(bot))

def add_to_bot(bot):
    """Ajouter les commandes crypto wallet au bot"""
    bot.add_cog(CryptoWalletCommands(bot))
    print("✅ Commandes Crypto Wallet chargées")
