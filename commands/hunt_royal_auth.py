"""
🏹 HUNT ROYAL AUTH SYSTEM - Arsenal Bot V4
==========================================

Système d'authentification pour Hunt Royal Calculator
- Commande /register pour les membres du clan
- Génération de tokens uniques pour l'accès au calculateur
- Vérification des membres du clan
"""

import discord
from discord import app_commands
import sqlite3
import secrets
import json
from discord.ext import commands
from datetime import datetime, timedelta

class HuntRoyalAuthDatabase:
    """Gestionnaire de base de données pour l'authentification Hunt Royal"""
    
    def __init__(self, db_path="hunt_royal_auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données d'authentification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunt_royal_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                access_token TEXT UNIQUE NOT NULL,
                clan_role TEXT DEFAULT 'member',
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                permissions TEXT DEFAULT 'calculator_access'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_member(self, discord_id, username, clan_role='member'):
        """Enregistrer un nouveau membre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer un token unique
            access_token = secrets.token_urlsafe(32)
            
            cursor.execute('''
                INSERT OR REPLACE INTO hunt_royal_members 
                (discord_id, username, access_token, clan_role, registered_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (discord_id, username, access_token, clan_role, datetime.now().isoformat()))
            
            conn.commit()
            return access_token
        except Exception as e:
            print(f"❌ Erreur enregistrement membre: {e}")
            return None
        finally:
            conn.close()
    
    def get_member_token(self, discord_id):
        """Récupérer le token d'un membre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT access_token, clan_role, is_active FROM hunt_royal_members WHERE discord_id = ?',
            (discord_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[2]:  # is_active
            return {"token": result[0], "role": result[1]}
        return None
    
    def validate_token(self, token):
        """Valider un token d'accès"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT discord_id, username, clan_role, permissions 
            FROM hunt_royal_members 
            WHERE access_token = ? AND is_active = 1
        ''', (token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "discord_id": result[0],
                "username": result[1],
                "clan_role": result[2],
                "permissions": result[3].split(',') if result[3] else []
            }
        return None
    
    def log_access(self, discord_id, action, ip_address=None, user_agent=None):
        """Logger un accès"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_logs (discord_id, action, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (discord_id, action, ip_address, user_agent))
        
        conn.commit()
        conn.close()

# Instance globale de la base de données
auth_db = HuntRoyalAuthDatabase()

@app_commands.command(name="register", description="S'enregistrer pour accéder au Hunt Royal Calculator")
async def register_hunt_royal(interaction: discord.Interaction):
    """Commande pour s'enregistrer au système Hunt Royal"""
    
    # Vérifier si l'utilisateur est dans le bon serveur/clan
    guild_id = interaction.guild_id
    user = interaction.user
    
    # Configuration des serveurs autorisés (à adapter selon votre clan)
    AUTHORIZED_GUILDS = [
        # Remplacez par l'ID de votre serveur Discord
        # 123456789012345678,  # Exemple d'ID de serveur
    ]
    
    # Pour le moment, on accepte tous les serveurs en développement
    # if guild_id not in AUTHORIZED_GUILDS:
    #     await interaction.response.send_message(
    #         "❌ Cette commande n'est disponible que pour les membres du clan Arsenal.",
    #         ephemeral=True
    #     )
    #     return
    
    # Vérifier les rôles de l'utilisateur pour déterminer son niveau
    clan_role = 'member'  # Par défaut
    
    if interaction.user.guild_permissions.administrator:
        clan_role = 'admin'
    elif any(role.name.lower() in ['moderator', 'mod', 'officer'] for role in user.roles):
        clan_role = 'moderator'
    elif any(role.name.lower() in ['vip', 'premium', 'elite'] for role in user.roles):
        clan_role = 'vip'
    
    # Enregistrer l'utilisateur
    access_token = auth_db.register_member(
        str(user.id),
        f"{user.name}#{user.discriminator}",
        clan_role
    )
    
    if access_token:
        # Logger l'enregistrement
        auth_db.log_access(str(user.id), "register")
        
        # Créer un embed de confirmation
        embed = discord.Embed(
            title="🏹 Hunt Royal - Enregistrement Réussi",
            description="Vous êtes maintenant enregistré pour utiliser le Hunt Royal Calculator !",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎯 Votre Token d'Accès",
            value=f"||`{access_token}`||",
            inline=False
        )
        
        embed.add_field(
            name="📊 Niveau d'Accès",
            value=f"**{clan_role.title()}**",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Accès au Calculator",
            value="[Hunt Royal Calculator](https://arsenal-webpanel.onrender.com/calculator)",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ Instructions",
            value="1. Gardez votre token secret\n2. Utilisez-le pour vous connecter au calculator\n3. En cas de problème, contactez un admin",
            inline=False
        )
        
        embed.set_footer(text="Token généré le")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Notification dans les logs (si channel configuré)
        print(f"✅ Nouvel enregistrement Hunt Royal: {user.name} ({clan_role})")
        
    else:
        embed = discord.Embed(
            title="❌ Erreur d'Enregistrement",
            description="Une erreur s'est produite lors de l'enregistrement. Contactez un administrateur.",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.command(name="mytoken", description="Récupérer votre token d'accès Hunt Royal")
async def get_my_token(interaction: discord.Interaction):
    """Récupérer le token de l'utilisateur"""
    
    user_data = auth_db.get_member_token(str(interaction.user.id))
    
    if user_data:
        embed = discord.Embed(
            title="🔑 Votre Token Hunt Royal",
            description="Voici votre token d'accès au calculator",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Token d'Accès",
            value=f"||`{user_data['token']}`||",
            inline=False
        )
        
        embed.add_field(
            name="📊 Niveau",
            value=f"**{user_data['role'].title()}**",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Calculator",
            value="[Accéder au Calculator](https://arsenal-webpanel.onrender.com/calculator)",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="❌ Non Enregistré",
            description="Vous n'êtes pas encore enregistré. Utilisez `/register` d'abord.",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Export des fonctions pour utilisation dans d'autres modules
__all__ = ['register_hunt_royal', 'get_my_token', 'auth_db', 'HuntRoyalAuthDatabase']
