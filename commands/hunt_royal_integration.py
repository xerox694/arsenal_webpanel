"""
🏹 HUNT ROYAL INTEGRATION SYSTEM - Arsenal Bot V4
================================================

Nouveau système d'intégration Hunt Royal avec calculator
- Commande /registerHR pour enregistrer ID de jeu Hunt Royal
- Génération de codes d'accès pour le calculator
- Intégration avec la base de données Hunt Royal unifiée
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import sys
import os

# Ajouter le chemin pour importer les modules Arsenal
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Arsenal_V4', 'webpanel', 'backend'))

try:
    from sqlite_database import ArsenalDatabase
except ImportError:
    print("⚠️ Module sqlite_database non trouvé")
    ArsenalDatabase = None

class HuntRoyalIntegration(commands.Cog):
    """Gestionnaire des commandes Hunt Royal Integration"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ArsenalDatabase() if ArsenalDatabase else None
    
    @app_commands.command(name="registerhr", description="🏹 Enregistrer votre ID Hunt Royal pour accéder au calculator")
    @app_commands.describe(
        hunt_royal_id="Votre ID de jeu Hunt Royal (exemple: 123456789)",
        username="Votre nom d'utilisateur Hunt Royal (optionnel)"
    )
    async def register_hunt_royal_id(
        self, 
        interaction: discord.Interaction, 
        hunt_royal_id: str,
        username: str = None
    ):
        """Enregistrer un compte Hunt Royal pour accéder au calculator"""
        
        if not self.db:
            await interaction.response.send_message(
                "❌ Base de données non disponible", 
                ephemeral=True
            )
            return
        
        try:
            # Valider l'ID Hunt Royal (format numérique basique)
            try:
                int(hunt_royal_id)
            except ValueError:
                await interaction.response.send_message(
                    "❌ **ID Hunt Royal invalide**\n"
                    "L'ID doit être un nombre (exemple: 123456789)",
                    ephemeral=True
                )
                return
            
            user_id = str(interaction.user.id)
            discord_username = interaction.user.display_name
            
            # Utiliser le username fourni ou le nom Discord
            final_username = username if username else discord_username
            
            # Vérifier si l'utilisateur a déjà un compte
            existing_account = self.db.get_hunt_royal_account(discord_user_id=user_id)
            
            if existing_account:
                # Mise à jour du compte existant
                embed = discord.Embed(
                    title="🏹 Compte Hunt Royal Existant",
                    description="Vous avez déjà un compte enregistré !",
                    color=0xFFD700
                )
                embed.add_field(
                    name="📋 Informations actuelles",
                    value=f"**Hunt Royal ID:** {existing_account['hunt_royal_id']}\n"
                          f"**Username:** {existing_account['username']}\n"
                          f"**Code d'accès:** `{existing_account['access_code']}`",
                    inline=False
                )
                embed.add_field(
                    name="🎯 Accès Calculator",
                    value="✅ Activé" if existing_account['calculator_access'] else "❌ Désactivé",
                    inline=True
                )
                embed.add_field(
                    name="🏆 Statistiques",
                    value=f"**Trophées:** {existing_account['trophies']}\n"
                          f"**Niveau:** {existing_account['level']}\n"
                          f"**Pièces:** {existing_account['coins']}",
                    inline=True
                )
                embed.set_footer(text="Utilisez ce code d'accès pour vous connecter au calculator")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Enregistrer nouveau compte
            access_code = self.db.register_hunt_royal_account(
                discord_user_id=user_id,
                hunt_royal_id=hunt_royal_id,
                username=final_username
            )
            
            if access_code:
                # Succès de l'enregistrement
                embed = discord.Embed(
                    title="🎉 Hunt Royal - Enregistrement Réussi !",
                    description="Votre compte Hunt Royal a été créé avec succès",
                    color=0x00FF00
                )
                embed.add_field(
                    name="🆔 Informations du compte",
                    value=f"**Discord:** {interaction.user.mention}\n"
                          f"**Hunt Royal ID:** {hunt_royal_id}\n"
                          f"**Username:** {final_username}",
                    inline=False
                )
                embed.add_field(
                    name="🔑 Code d'accès Calculator",
                    value=f"```{access_code}```",
                    inline=False
                )
                embed.add_field(
                    name="📊 Comment utiliser",
                    value="1️⃣ Allez sur le Hunt Royal Calculator\n"
                          "2️⃣ Utilisez ce code d'accès pour vous connecter\n"
                          "3️⃣ Profitez des fonctionnalités avancées !",
                    inline=False
                )
                embed.add_field(
                    name="🔗 Liens utiles",
                    value="[Calculator](https://arsenal-webpanel.onrender.com) • [Documentation](https://github.com/Arsenal-Discord-Bot)",
                    inline=False
                )
                embed.set_footer(
                    text="⚠️ Gardez ce code secret et ne le partagez avec personne !",
                    icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                # Log de l'enregistrement
                print(f"✅ Nouveau compte Hunt Royal: {interaction.user} ({user_id}) -> {hunt_royal_id}")
                
            else:
                await interaction.response.send_message(
                    "❌ **Erreur lors de l'enregistrement**\n"
                    "Veuillez réessayer plus tard ou contactez un administrateur.",
                    ephemeral=True
                )
                
        except Exception as e:
            print(f"❌ Erreur registerHR: {e}")
            await interaction.response.send_message(
                "❌ **Erreur technique**\n"
                "Une erreur est survenue lors de l'enregistrement.",
                ephemeral=True
            )
    
    @app_commands.command(name="myhrcode", description="🔑 Récupérer votre code d'accès Hunt Royal Calculator")
    async def get_my_hr_code(self, interaction: discord.Interaction):
        """Récupérer le code d'accès Hunt Royal de l'utilisateur"""
        
        if not self.db:
            await interaction.response.send_message(
                "❌ Base de données non disponible", 
                ephemeral=True
            )
            return
        
        try:
            user_id = str(interaction.user.id)
            account = self.db.get_hunt_royal_account(discord_user_id=user_id)
            
            if account:
                embed = discord.Embed(
                    title="🔑 Votre Code d'Accès Hunt Royal",
                    color=0x00BFFF
                )
                embed.add_field(
                    name="📋 Informations du compte",
                    value=f"**Hunt Royal ID:** {account['hunt_royal_id']}\n"
                          f"**Username:** {account['username']}\n"
                          f"**Enregistré:** <t:{int(account['created_at'].timestamp())}:R>" if account.get('created_at') else "N/A",
                    inline=False
                )
                embed.add_field(
                    name="🔑 Code d'accès",
                    value=f"```{account['access_code']}```",
                    inline=False
                )
                embed.add_field(
                    name="🎯 Statut Calculator",
                    value="✅ Accès autorisé" if account['calculator_access'] else "❌ Accès désactivé",
                    inline=True
                )
                embed.add_field(
                    name="🏆 Statistiques",
                    value=f"**Trophées:** {account['trophies']}\n"
                          f"**Niveau:** {account['level']}\n"
                          f"**Pièces:** {account['coins']}",
                    inline=True
                )
                embed.set_footer(text="Gardez ce code secret !")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Aucun Compte Hunt Royal",
                    description="Vous n'avez pas encore enregistré de compte Hunt Royal.",
                    color=0xFF0000
                )
                embed.add_field(
                    name="📝 Comment s'enregistrer",
                    value="Utilisez la commande `/registerhr` avec votre ID Hunt Royal",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            print(f"❌ Erreur myhrcode: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la récupération du code",
                ephemeral=True
            )
    
    @app_commands.command(name="hrstats", description="📊 [ADMIN] Statistiques du système Hunt Royal")
    @app_commands.default_permissions(administrator=True)
    async def hunt_royal_admin_stats(self, interaction: discord.Interaction):
        """Statistiques administrateur du système Hunt Royal"""
        
        if not self.db:
            await interaction.response.send_message(
                "❌ Base de données non disponible", 
                ephemeral=True
            )
            return
        
        # Vérifier les permissions admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Permission insuffisante (Admin requis)",
                ephemeral=True
            )
            return
        
        try:
            # Récupérer les statistiques depuis la base de données
            # Note: Ces méthodes devront être ajoutées à sqlite_database.py
            
            embed = discord.Embed(
                title="📊 Statistiques Hunt Royal System",
                description="Statistiques globales du système d'intégration",
                color=0x8A2BE2
            )
            
            # Placeholder - à implémenter dans sqlite_database.py
            embed.add_field(
                name="👥 Comptes enregistrés",
                value="Statistiques non disponibles\n(Méthodes à implémenter)",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Statut système",
                value="✅ Base de données connectée\n✅ APIs fonctionnelles",
                inline=True
            )
            
            embed.set_footer(text="Arsenal Bot V4 - Hunt Royal Integration")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ Erreur hrstats: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la récupération des statistiques",
                ephemeral=True
            )

async def setup(bot):
    """Fonction de setup pour le cog"""
    await bot.add_cog(HuntRoyalIntegration(bot))

# Export pour utilisation directe
__all__ = ['HuntRoyalIntegration', 'setup']
