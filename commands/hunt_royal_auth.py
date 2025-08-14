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
        """Initialiser la base de données d'authentification ultra-avancée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunt_royal_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT,
                access_token TEXT UNIQUE NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                clan_role TEXT DEFAULT 'member',
                clan_name TEXT,
                game_id_new TEXT,
                game_id_old TEXT,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                login_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                permissions TEXT DEFAULT 'calculator_access',
                clan_permissions TEXT DEFAULT 'basic_access',
                security_level INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                success INTEGER DEFAULT 1,
                details TEXT,
                security_flags TEXT
            )
        ''')
        
        # Table pour les clans et leur hiérarchie
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clan_hierarchy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_name TEXT NOT NULL,
                discord_id TEXT NOT NULL,
                role_level INTEGER NOT NULL,
                role_name TEXT NOT NULL,
                permissions TEXT DEFAULT 'basic',
                appointed_by TEXT,
                appointed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                UNIQUE(clan_name, discord_id)
            )
        ''')
        
        # Table pour les sessions et la sécurité
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                security_flags TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_member(self, discord_id, username, clan_role='member', game_id_new=None, game_id_old=None, clan_name=None):
        """Enregistrer un nouveau membre avec informations complètes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer un token unique ET un code court
            access_token = secrets.token_urlsafe(32)
            short_code = self.generate_short_code()
            
            cursor.execute('''
                INSERT OR REPLACE INTO hunt_royal_members 
                (discord_id, username, display_name, access_token, short_code, clan_role, game_id_new, game_id_old, clan_name, registered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (discord_id, username, username, access_token, short_code, clan_role, game_id_new, game_id_old, clan_name, datetime.now().isoformat()))
            
            conn.commit()
            return {
                "token": access_token,
                "short_code": short_code,
                "success": True
            }
        except Exception as e:
            print(f"❌ Erreur enregistrement membre: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def generate_short_code(self):
        """Générer un code court de 7-10 chiffres unique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        max_attempts = 100
        for _ in range(max_attempts):
            # Générer code de 7 à 10 chiffres
            code_length = secrets.randbelow(4) + 7  # 7-10 chiffres
            short_code = ''.join([str(secrets.randbelow(10)) for _ in range(code_length)])
            
            # Vérifier unicité
            cursor.execute('SELECT COUNT(*) FROM hunt_royal_members WHERE short_code = ?', (short_code,))
            if cursor.fetchone()[0] == 0:
                conn.close()
                return short_code
        
        conn.close()
        # Fallback avec timestamp si collision
        return str(int(datetime.now().timestamp()))[-8:]
    
    def get_member_token(self, discord_id):
        """Récupérer le token d'un membre avec informations complètes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT access_token, short_code, clan_role, game_id_new, game_id_old, 
                   clan_name, display_name, login_count, is_active 
            FROM hunt_royal_members 
            WHERE discord_id = ?
        ''', (discord_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[8]:  # is_active
            return {
                "token": result[0],
                "short_code": result[1], 
                "role": result[2],
                "game_id_new": result[3],
                "game_id_old": result[4],
                "clan_name": result[5],
                "display_name": result[6],
                "login_count": result[7]
            }
        return None
    
    def validate_token_or_code(self, identifier, username=None):
        """Valider soit un token complet, soit un code court + nom d'utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Essayer d'abord comme token complet
        cursor.execute('''
            SELECT discord_id, username, display_name, clan_role, permissions, short_code,
                   game_id_new, game_id_old, clan_name
            FROM hunt_royal_members 
            WHERE access_token = ? AND is_active = 1
        ''', (identifier,))
        
        result = cursor.fetchone()
        
        # Si pas trouvé comme token, essayer comme code court
        if not result and username:
            cursor.execute('''
                SELECT discord_id, username, display_name, clan_role, permissions, short_code,
                       game_id_new, game_id_old, clan_name
                FROM hunt_royal_members 
                WHERE short_code = ? AND (username LIKE ? OR display_name LIKE ?) AND is_active = 1
            ''', (identifier, f"%{username}%", f"%{username}%"))
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                "discord_id": result[0],
                "username": result[1],
                "display_name": result[2] or result[1],
                "clan_role": result[3],
                "permissions": result[4].split(',') if result[4] else [],
                "short_code": result[5],
                "game_id_new": result[6],
                "game_id_old": result[7],
                "clan_name": result[8],
                "login_method": "token" if len(identifier) > 10 else "code"
            }
        return None
    
    def regenerate_tokens(self, discord_id):
        """Régénérer à la fois le token et le code court"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer nouveaux token et code
            new_token = secrets.token_urlsafe(32)
            new_short_code = self.generate_short_code()
            
            cursor.execute('''
                UPDATE hunt_royal_members 
                SET access_token = ?, short_code = ?, last_login = ?
                WHERE discord_id = ? AND is_active = 1
            ''', (new_token, new_short_code, datetime.now().isoformat(), discord_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.log_access(discord_id, "tokens_regenerated", details=f"New code: {new_short_code}")
                return {
                    "success": True,
                    "new_token": new_token,
                    "new_short_code": new_short_code
                }
            else:
                return {"success": False, "error": "Utilisateur non trouvé"}
        except Exception as e:
            print(f"❌ Erreur régénération tokens: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def get_user_statistics(self, discord_id):
        """Récupérer les statistiques détaillées d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Infos de base
        cursor.execute('''
            SELECT username, display_name, clan_role, game_id_new, game_id_old, 
                   clan_name, registered_at, last_login, login_count
            FROM hunt_royal_members 
            WHERE discord_id = ? AND is_active = 1
        ''', (discord_id,))
        user_info = cursor.fetchone()
        
        if not user_info:
            conn.close()
            return None
        
        # Logs d'accès récents
        cursor.execute('''
            SELECT action, timestamp, ip_address, success, details
            FROM access_logs 
            WHERE discord_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (discord_id,))
        recent_logs = cursor.fetchall()
        
        # Statistiques d'accès
        cursor.execute('''
            SELECT COUNT(*) as total_access,
                   COUNT(CASE WHEN success = 1 THEN 1 END) as successful_access,
                   COUNT(CASE WHEN action LIKE '%calculator%' THEN 1 END) as calculator_usage
            FROM access_logs 
            WHERE discord_id = ?
        ''', (discord_id,))
        access_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "user_info": user_info,
            "recent_logs": recent_logs,
            "access_stats": access_stats
        }
    
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

@app_commands.command(name="register", description="S'enregistrer pour accéder au Hunt Royal Calculator avec GUI avancé")
async def register_hunt_royal(interaction: discord.Interaction):
    """Commande avancée pour s'enregistrer au système Hunt Royal avec Modal GUI"""
    
    user = interaction.user
    user_id = str(user.id)
    
    # 🔐 ÉTAPE 1: Vérifications de sécurité rapides
    existing_member = auth_db.get_member_token(user_id)
    if existing_member:
        view = TokenManagementView(existing_member['token'], existing_member.get('short_code', 'N/A'), user_id)
        embed = discord.Embed(
            title="⚠️ Déjà Enregistré",
            description="Vous êtes déjà enregistré dans le système Hunt Royal !",
            color=discord.Color.orange()
        )
        embed.add_field(name="🎯 Token", value=f"||`{existing_member['token']}`||", inline=False)
        embed.add_field(name="� Code Court", value=f"**{existing_member.get('short_code', 'N/A')}**", inline=True)
        embed.add_field(name="� Niveau", value=f"**{existing_member['role'].title()}**", inline=True)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        return
    
    # Vérifications de sécurité avancées
    account_age = (interaction.created_at - user.created_at).days
    member = interaction.guild.get_member(user.id)
    server_join_days = (interaction.created_at - member.joined_at).days if member and member.joined_at else 0
    
    if account_age < 7:
        embed = discord.Embed(
            title="🛡️ Sécurité - Compte Trop Récent",
            description=f"Votre compte Discord doit avoir au moins 7 jours.\n**Âge actuel:** {account_age} jour(s)",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if server_join_days < 1:
        embed = discord.Embed(
            title="🛡️ Sécurité - Nouveau Membre",
            description=f"Vous devez être membre du serveur depuis au moins 24h.\n**Sur le serveur depuis:** {server_join_days} jour(s)",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Ouvrir le modal de registration
    modal = HuntRoyalRegistrationModal()
    await interaction.response.send_modal(modal)

class HuntRoyalRegistrationModal(discord.ui.Modal, title='🏹 Registration Hunt Royal - Informations Clan'):
    """Modal avancé pour l'enregistrement Hunt Royal"""
    
    def __init__(self):
        super().__init__(timeout=300)  # 5 minutes timeout
    
    # ID de jeu actuel (OBLIGATOIRE)
    game_id_new = discord.ui.TextInput(
        label='🎯 ID de jeu Hunt Royal (OBLIGATOIRE)',
        placeholder='Votre ID de jeu Hunt Royal actuel...',
        required=True,
        max_length=50
    )
    
    # ID de jeu ancien (OPTIONNEL)
    game_id_old = discord.ui.TextInput(
        label='� Ancien ID de jeu (optionnel)',
        placeholder='Votre ancien ID si vous en aviez un...',
        required=False,
        max_length=50
    )
    
    # Nom du clan (OPTIONNEL)
    clan_name = discord.ui.TextInput(
        label='🏰 Nom de votre Clan (optionnel)',
        placeholder='Le nom de votre clan Hunt Royal...',
        required=False,
        max_length=100
    )
    
    # Nom d'utilisateur préféré (OPTIONNEL)
    display_name = discord.ui.TextInput(
        label='👤 Nom d\'affichage préféré (optionnel)',
        placeholder='Comment voulez-vous être appelé ?',
        required=False,
        max_length=50
    )
    
    # Notes additionnelles (OPTIONNEL)
    additional_notes = discord.ui.TextInput(
        label='📝 Notes additionnelles (optionnel)',
        placeholder='Rang dans le clan, informations spéciales...',
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Traitement du formulaire de registration"""
        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        user_id = str(user.id)
        member = interaction.guild.get_member(user.id)
        
        # Analyse des rôles et permissions
        clan_role, access_level, role_perks = analyze_user_permissions(member)
        
        # Enregistrement avec toutes les informations
        result = auth_db.register_member(
            discord_id=user_id,
            username=f"{user.name}#{user.discriminator}",
            clan_role=clan_role,
            game_id_new=self.game_id_new.value,
            game_id_old=self.game_id_old.value or None,
            clan_name=self.clan_name.value or None
        )
        
        if not result.get("success"):
            embed = discord.Embed(
                title="❌ Erreur Système",
                description=f"Erreur lors de l'enregistrement: {result.get('error', 'Erreur inconnue')}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Logger l'enregistrement
        auth_db.log_access(user_id, f"register_success_{clan_role}")
        
        # Créer l'embed de confirmation ultra-détaillé
        embed = discord.Embed(
            title="🏹 Hunt Royal - Enregistrement Réussi !",
            description=f"Bienvenue dans le système Hunt Royal, **{self.display_name.value or user.display_name}** !",
            color=discord.Color.green()
        )
        
        # Informations utilisateur
        embed.add_field(
            name="👤 Profil Utilisateur",
            value=f"**Discord:** {user.display_name}\n**ID:** {user_id}\n**Niveau:** {clan_role.title()}\n**Accès:** Niveau {access_level}",
            inline=True
        )
        
        # Informations Hunt Royal
        hunt_info = f"**ID Jeu:** {self.game_id_new.value}"
        if self.game_id_old.value:
            hunt_info += f"\n**Ancien ID:** {self.game_id_old.value}"
        if self.clan_name.value:
            hunt_info += f"\n**Clan:** {self.clan_name.value}"
        
        embed.add_field(name="🎯 Hunt Royal", value=hunt_info, inline=True)
        
        # Token et Code Court
        embed.add_field(
            name="🔑 Accès Sécurisé",
            value=f"**Token:** ||`{result['token']}`||\n**Code Court:** `{result['short_code']}`\n⚠️ **Gardez-les secrets !**",
            inline=False
        )
        
        # Privilèges
        embed.add_field(
            name="🎯 Vos Privilèges",
            value="\n".join([f"• {perk}" for perk in role_perks]),
            inline=True
        )
        
        # Instructions d'utilisation
        embed.add_field(
            name="📋 Comment se connecter",
            value=f"""
            **Méthode 1 - Token complet:**
            Utilisez: ||`{result['token']}`||
            
            **Méthode 2 - Code court + nom:**
            Code: `{result['short_code']}`
            Nom: `{user.display_name}`
            
            **🌐 Calculator:** [Hunt Royal Calculator](https://arsenal-webpanel.onrender.com/calculator)
            """,
            inline=False
        )
        
        if self.additional_notes.value:
            embed.add_field(name="📝 Notes", value=self.additional_notes.value, inline=False)
        
        embed.set_footer(text=f"� Enregistré le {interaction.created_at.strftime('%d/%m/%Y à %H:%M')} • Gardez vos codes privés !")
        embed.timestamp = interaction.created_at
        
        # Créer les boutons de gestion
        view = TokenManagementView(result['token'], result['short_code'], user_id)
        
        await interaction.followup.send(embed=embed, view=view)
        
        print(f"✅ [HUNT ROYAL] Nouvel enregistrement: {user.display_name} ({clan_role}) - Game ID: {self.game_id_new.value}")

def analyze_user_permissions(member):
    """Analyser les permissions d'un utilisateur"""
    if not member:
        return 'member', 1, ["Accès de base"]
    
    user_roles = [role.name.lower() for role in member.roles]
    
    if member.guild_permissions.administrator:
        return 'admin', 4, ["Accès illimité", "Gestion des tokens", "Analytics avancées", "Support prioritaire"]
    elif any(role in ['moderator', 'mod', 'officer', 'modo'] for role in user_roles):
        return 'moderator', 3, ["Accès étendu", "Fonctions avancées", "Support prioritaire"]
    elif any(role in ['vip', 'premium', 'elite', 'booster'] for role in user_roles):
        return 'vip', 2, ["Accès premium", "Fonctions exclusives", "Priorité"]
    
    perks = ["Accès de base", "Calculateur standard"]
    clan_role = 'member'
    
    if member.premium_since:
        perks.append("Bonus Nitro Booster")
        clan_role = 'vip'
    
    return clan_role, 1, perks

class TokenManagementView(discord.ui.View):
    """Vue avec boutons pour gérer les tokens"""
    
    def __init__(self, token, short_code, user_id):
        super().__init__(timeout=3600)  # 1 heure
        self.token = token
        self.short_code = short_code
        self.user_id = user_id
    
    @discord.ui.button(label='� Copier Token', style=discord.ButtonStyle.primary, emoji='📋')
    async def copy_token(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour copier le token"""
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas votre token !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="� Token Copié",
            description=f"**Token complet:**\n```{self.token}```\n\n**Code court:**\n```{self.short_code}```",
            color=discord.Color.blue()
        )
        embed.set_footer(text="⚠️ Ne partagez jamais ces codes avec personne !")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label='🔄 Régénérer', style=discord.ButtonStyle.secondary, emoji='🔄')
    async def regenerate_token(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour régénérer le token"""
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas votre token !", ephemeral=True)
            return
        
        # Ici on appellerait la méthode de régénération
        await interaction.response.send_message("🔄 Fonction de régénération en cours d'implémentation...", ephemeral=True)
    
    @discord.ui.button(label='📊 Mes Stats', style=discord.ButtonStyle.success, emoji='📊')
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour voir les statistiques"""
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Ce ne sont pas vos stats !", ephemeral=True)
            return
        
        # Ici on afficherait les statistiques détaillées
        await interaction.response.send_message("📊 Fonction de statistiques en cours d'implémentation...", ephemeral=True)

@app_commands.command(name="mytoken", description="Récupérer votre token d'accès Hunt Royal avec gestion avancée")
async def get_my_token(interaction: discord.Interaction):
    """Récupérer le token de l'utilisateur avec boutons de gestion"""
    
    user_data = auth_db.get_member_token(str(interaction.user.id))
    
    if user_data:
        # Créer la vue avec boutons de gestion
        view = TokenManagementView(
            user_data['token'], 
            user_data.get('short_code', 'N/A'), 
            str(interaction.user.id)
        )
        
        embed = discord.Embed(
            title="🔑 Votre Token Hunt Royal",
            description="Voici vos informations d'accès au Hunt Royal Calculator",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Token d'Accès Complet",
            value=f"||`{user_data['token']}`||",
            inline=False
        )
        
        embed.add_field(
            name="� Code Court",
            value=f"**{user_data.get('short_code', 'N/A')}**",
            inline=True
        )
        
        embed.add_field(
            name="�📊 Niveau d'Accès",
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
            value="⚠️ Ne partagez jamais vos codes !\n🔄 Utilisez les boutons ci-dessous pour gérer",
            inline=False
        )
        
        embed.add_field(
            name="📋 Comment se connecter",
            value=f"""**Méthode 1:** Copiez le token complet
            **Méthode 2:** Code court `{user_data.get('short_code', 'N/A')}` + votre nom Discord""",
            inline=False
        )
        
        embed.set_footer(text="Token confidentiel • Arsenal Hunt Royal System")
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else:
        embed = discord.Embed(
            title="❌ Non Enregistré",
            description="Vous n'êtes pas encore enregistré dans le système Hunt Royal.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🚀 Pour commencer",
            value="Utilisez la commande `/register` pour vous enregistrer avec le nouveau système GUI",
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
