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
    """Commande avancée pour s'enregistrer au système Hunt Royal"""
    
    await interaction.response.defer(ephemeral=True)
    
    guild_id = interaction.guild_id
    user = interaction.user
    user_id = str(user.id)
    
    # 🔐 ÉTAPE 1: Vérifications de sécurité avancées
    
    # Vérifier si l'utilisateur est déjà enregistré
    existing_member = auth_db.get_member_token(user_id)
    if existing_member:
        embed = discord.Embed(
            title="⚠️ Déjà Enregistré",
            description="Vous êtes déjà enregistré dans le système Hunt Royal !",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="🎯 Votre Token",
            value=f"||`{existing_member['token']}`||",
            inline=False
        )
        embed.add_field(
            name="📊 Niveau Actuel",
            value=f"**{existing_member['role'].title()}**",
            inline=True
        )
        embed.add_field(
            name="💡 Astuce",
            value="Utilisez `/mytoken` pour récupérer vos informations",
            inline=True
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Vérifier l'ancienneté du compte Discord (anti-spam)
    account_age = (interaction.created_at - user.created_at).days
    if account_age < 7:  # Compte de moins de 7 jours
        embed = discord.Embed(
            title="🛡️ Sécurité - Compte Trop Récent",
            description="Votre compte Discord doit avoir au moins 7 jours pour s'enregistrer.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="📅 Âge de votre compte",
            value=f"{account_age} jour(s)",
            inline=True
        )
        embed.add_field(
            name="⏰ Requis",
            value="7 jours minimum",
            inline=True
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Vérifier la présence sur le serveur (anti-raid)
    member = interaction.guild.get_member(user.id)
    if not member:
        embed = discord.Embed(
            title="❌ Erreur - Membre Introuvable",
            description="Impossible de vérifier votre statut sur ce serveur.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    server_join_days = (interaction.created_at - member.joined_at).days if member.joined_at else 0
    if server_join_days < 1:  # Nouveau sur le serveur
        embed = discord.Embed(
            title="🛡️ Sécurité - Nouveau Membre",
            description="Vous devez être membre du serveur depuis au moins 24h.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="📅 Sur le serveur depuis",
            value=f"{server_join_days} jour(s)",
            inline=True
        )
        await interaction.followup.send(embed=embed)
        return
    
    # 🎯 ÉTAPE 2: Analyse des rôles et permissions
    
    clan_role = 'member'  # Par défaut
    role_perks = []
    access_level = 1
    
    # Analyse des rôles Discord
    user_roles = [role.name.lower() for role in member.roles]
    
    if member.guild_permissions.administrator:
        clan_role = 'admin'
        access_level = 4
        role_perks = ["Accès illimité", "Gestion des tokens", "Analytics avancées", "Support prioritaire"]
    elif any(role in ['moderator', 'mod', 'officer', 'modo'] for role in user_roles):
        clan_role = 'moderator'
        access_level = 3
        role_perks = ["Accès étendu", "Fonctions avancées", "Support prioritaire"]
    elif any(role in ['vip', 'premium', 'elite', 'booster'] for role in user_roles):
        clan_role = 'vip'
        access_level = 2
        role_perks = ["Accès premium", "Fonctions exclusives", "Priorité"]
    else:
        role_perks = ["Accès de base", "Calculateur standard"]
    
    # Bonus pour les Nitro boosters
    if member.premium_since:
        clan_role = 'vip' if clan_role == 'member' else clan_role
        role_perks.append("Bonus Nitro Booster")
    
    # 🏹 ÉTAPE 3: Création du profil avancé
    
    access_token = auth_db.register_member(user_id, f"{user.name}#{user.discriminator}", clan_role)
    
    if not access_token:
        embed = discord.Embed(
            title="❌ Erreur Système",
            description="Une erreur s'est produite lors de l'enregistrement. Contactez un administrateur.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Logger l'enregistrement avec détails
    auth_db.log_access(user_id, f"register_success_{clan_role}")
    
    # 🎉 ÉTAPE 4: Réponse détaillée et informative
    
    embed = discord.Embed(
        title="🏹 Hunt Royal - Enregistrement Réussi !",
        description=f"Bienvenue dans le système Hunt Royal, **{user.display_name}** !",
        color=discord.Color.green()
    )
    
    # Informations utilisateur
    embed.add_field(
        name="👤 Profil Utilisateur",
        value=f"**Nom:** {user.display_name}\n**ID:** {user_id}\n**Niveau:** {clan_role.title()}",
        inline=True
    )
    
    # Informations compte
    embed.add_field(
        name="📊 Informations Compte",
        value=f"**Ancienneté:** {account_age} jours\n**Sur serveur:** {server_join_days} jours\n**Accès:** Niveau {access_level}",
        inline=True
    )
    
    # Token sécurisé
    embed.add_field(
        name="🔑 Token d'Accès Sécurisé",
        value=f"||`{access_token}`||\n⚠️ **Gardez-le secret !**",
        inline=False
    )
    
    # Privilèges et fonctionnalités
    embed.add_field(
        name="🎯 Vos Privilèges",
        value="\n".join([f"• {perk}" for perk in role_perks]),
        inline=True
    )
    
    # Liens et accès
    embed.add_field(
        name="🌐 Accès Webpanel",
        value="[Hunt Royal Calculator](https://arsenal-webpanel.onrender.com/calculator)\n[Dashboard](https://arsenal-webpanel.onrender.com/)",
        inline=True
    )
    
    # Instructions détaillées
    embed.add_field(
        name="📋 Instructions d'Utilisation",
        value="""
        **1.** Copiez votre token (cliquez sur le texte caché)
        **2.** Allez sur le [Calculator](https://arsenal-webpanel.onrender.com/calculator)
        **3.** Collez votre token dans le champ de connexion
        **4.** Profitez des fonctionnalités Hunt Royal !
        
        **Commandes utiles:**
        • `/mytoken` - Récupérer votre token
        • `/link-hunt` - Lier votre profil Hunt Royal
        • `/profile-hunt` - Voir votre profil
        """,
        inline=False
    )
    
    # Footer avec informations de sécurité
    embed.set_footer(
        text=f"🔐 Token généré le {interaction.created_at.strftime('%d/%m/%Y à %H:%M')} • Gardez votre token privé !"
    )
    embed.timestamp = interaction.created_at
    
    await interaction.followup.send(embed=embed)
    
    # 📊 ÉTAPE 5: Notification dans les logs (si configuré)
    print(f"✅ [HUNT ROYAL] Nouvel enregistrement: {user.display_name} ({clan_role}) - Server: {interaction.guild.name}")
    
    # Optionnel: Notification dans un canal de logs
    # log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
    # if log_channel:
    #     log_embed = discord.Embed(
    #         title="📊 Nouvel Enregistrement Hunt Royal",
    #         description=f"**{user.display_name}** s'est enregistré",
    #         color=discord.Color.blue()
    #     )
    #     await log_channel.send(embed=log_embed)

@app_commands.command(name="mytoken", description="Récupérer votre token d'accès Hunt Royal")
async def get_my_token(interaction: discord.Interaction):
    """Récupérer le token de l'utilisateur avec informations détaillées"""
    
    user_data = auth_db.get_member_token(str(interaction.user.id))
    
    if user_data:
        embed = discord.Embed(
            title="🔑 Votre Token Hunt Royal",
            description="Voici vos informations d'accès au Hunt Royal Calculator",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Token d'Accès",
            value=f"||`{user_data['token']}`||",
            inline=False
        )
        
        embed.add_field(
            name="📊 Niveau d'Accès",
            value=f"**{user_data['role'].title()}**",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Calculator",
            value="[Accéder au Calculator](https://arsenal-webpanel.onrender.com/calculator)",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Sécurité",
            value="⚠️ Ne partagez jamais votre token !\n🔄 Régénération possible via admin",
            inline=False
        )
        
        embed.set_footer(text="Token confidentiel • Arsenal Hunt Royal System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="❌ Non Enregistré",
            description="Vous n'êtes pas encore enregistré dans le système Hunt Royal.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🚀 Pour commencer",
            value="Utilisez la commande `/register` pour vous enregistrer",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.command(name="hunt-stats", description="[ADMIN] Statistiques du système Hunt Royal")
async def hunt_royal_stats(interaction: discord.Interaction):
    """Commande admin pour voir les statistiques du système"""
    
    # Vérifier les permissions admin
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="🔒 Accès Refusé",
            description="Cette commande est réservée aux administrateurs.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Récupérer les statistiques de la base de données
    conn = sqlite3.connect(auth_db.db_path)
    cursor = conn.cursor()
    
    # Statistiques générales
    cursor.execute('SELECT COUNT(*) FROM hunt_royal_members WHERE is_active = 1')
    total_members = cursor.fetchone()[0]
    
    cursor.execute('SELECT clan_role, COUNT(*) FROM hunt_royal_members WHERE is_active = 1 GROUP BY clan_role')
    role_stats = dict(cursor.fetchall())
    
    cursor.execute('SELECT COUNT(*) FROM access_logs WHERE action LIKE "register%" AND date(timestamp) = date("now")')
    today_registrations = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM access_logs WHERE date(timestamp) >= date("now", "-7 days")')
    week_activity = cursor.fetchone()[0]
    
    # Derniers enregistrements
    cursor.execute('''
        SELECT username, clan_role, registered_at 
        FROM hunt_royal_members 
        WHERE is_active = 1 
        ORDER BY registered_at DESC 
        LIMIT 5
    ''')
    recent_members = cursor.fetchall()
    
    conn.close()
    
    # Créer l'embed de statistiques
    embed = discord.Embed(
        title="📊 Hunt Royal - Statistiques Système",
        description="Vue d'ensemble du système d'authentification Hunt Royal",
        color=discord.Color.blue()
    )
    
    # Stats générales
    embed.add_field(
        name="👥 Membres Actifs",
        value=f"**{total_members}** membres enregistrés",
        inline=True
    )
    
    embed.add_field(
        name="📈 Activité",
        value=f"**{today_registrations}** aujourd'hui\n**{week_activity}** cette semaine",
        inline=True
    )
    
    # Répartition par rôles
    role_display = []
    role_emojis = {"admin": "👑", "moderator": "🛡️", "vip": "⭐", "member": "👤"}
    for role, count in role_stats.items():
        emoji = role_emojis.get(role, "👤")
        role_display.append(f"{emoji} **{role.title()}**: {count}")
    
    embed.add_field(
        name="🎯 Répartition par Rôles",
        value="\n".join(role_display) if role_display else "Aucun membre",
        inline=False
    )
    
    # Derniers membres
    if recent_members:
        recent_display = []
        for username, role, registered_at in recent_members:
            date_str = registered_at[:10]  # Format YYYY-MM-DD
            emoji = role_emojis.get(role, "👤")
            recent_display.append(f"{emoji} **{username}** ({role}) - {date_str}")
        
        embed.add_field(
            name="🆕 Derniers Enregistrements",
            value="\n".join(recent_display),
            inline=False
        )
    
    embed.set_footer(text="Hunt Royal Admin Panel • Arsenal Bot V4")
    embed.timestamp = interaction.created_at
    
    await interaction.followup.send(embed=embed)

# Export des fonctions pour utilisation dans d'autres modules
__all__ = ['register_hunt_royal', 'get_my_token', 'hunt_royal_stats', 'auth_db', 'HuntRoyalAuthDatabase']
