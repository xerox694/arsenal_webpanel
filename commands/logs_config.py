"""
🔧 LOGS CONFIG SYSTEM - Arsenal Bot V4
=====================================

Système de configuration des logs avancé pour les administrateurs de serveur
Style DraftBot mais avec plus de fonctionnalités
"""

import discord
from discord.ext import commands
import sqlite3
import json
from datetime import datetime
import asyncio

class LogsConfigModal(discord.ui.Modal):
    """Modal de configuration des logs avancé"""
    
    def __init__(self, guild_id: int, current_config: dict = None):
        super().__init__(title="🔧 Configuration des Logs - Arsenal Bot")
        self.guild_id = guild_id
        self.current_config = current_config or {}
        
        # Canal principal des logs
        self.log_channel = discord.ui.TextInput(
            label="📝 Canal Principal des Logs",
            placeholder="ID du canal ou #nom-du-canal",
            default=str(self.current_config.get('main_channel', '')),
            max_length=100,
            required=True
        )
        
        # Types de logs activés
        self.log_types = discord.ui.TextInput(
            label="📋 Types de Logs (séparés par des virgules)",
            placeholder="join,leave,ban,kick,message_delete,voice,role_update",
            default=','.join(self.current_config.get('enabled_types', [])),
            max_length=500,
            required=False,
            style=discord.TextStyle.paragraph
        )
        
        # Canaux spécialisés
        self.specialized_channels = discord.ui.TextInput(
            label="🎯 Canaux Spécialisés (format: type:canal_id)",
            placeholder="moderation:123456,voice:789012,economy:345678",
            default=','.join([f"{k}:{v}" for k, v in self.current_config.get('specialized_channels', {}).items()]),
            max_length=500,
            required=False,
            style=discord.TextStyle.paragraph
        )
        
        # Filtres et exclusions
        self.filters = discord.ui.TextInput(
            label="🚫 Exclusions (IDs utilisateurs/rôles/canaux)",
            placeholder="user:123456,role:789012,channel:345678",
            default=','.join([f"{k}:{v}" for k, v in self.current_config.get('filters', {}).items()]),
            max_length=500,
            required=False,
            style=discord.TextStyle.paragraph
        )
        
        # Configuration avancée
        self.advanced_config = discord.ui.TextInput(
            label="⚙️ Config Avancée (JSON)",
            placeholder='{"embed_color": "orange", "mention_admins": true, "auto_delete": 24}',
            default=json.dumps(self.current_config.get('advanced', {}), indent=2),
            max_length=1000,
            required=False,
            style=discord.TextStyle.paragraph
        )
        
        # Ajouter tous les champs
        self.add_item(self.log_channel)
        self.add_item(self.log_types)
        self.add_item(self.specialized_channels)
        self.add_item(self.filters)
        self.add_item(self.advanced_config)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traitement de la soumission du modal"""
        try:
            # Parser les données
            config_data = {
                'guild_id': self.guild_id,
                'main_channel': self.log_channel.value.strip(),
                'enabled_types': [t.strip() for t in self.log_types.value.split(',') if t.strip()],
                'specialized_channels': {},
                'filters': {},
                'advanced': {},
                'updated_at': datetime.now().isoformat(),
                'updated_by': str(interaction.user.id)
            }
            
            # Parser canaux spécialisés
            if self.specialized_channels.value:
                for item in self.specialized_channels.value.split(','):
                    if ':' in item:
                        log_type, channel_id = item.split(':', 1)
                        config_data['specialized_channels'][log_type.strip()] = channel_id.strip()
            
            # Parser filtres
            if self.filters.value:
                for item in self.filters.value.split(','):
                    if ':' in item:
                        filter_type, filter_id = item.split(':', 1)
                        config_data['filters'][filter_type.strip()] = filter_id.strip()
            
            # Parser config avancée JSON
            if self.advanced_config.value.strip():
                try:
                    config_data['advanced'] = json.loads(self.advanced_config.value)
                except json.JSONDecodeError:
                    config_data['advanced'] = {"error": "JSON invalide"}
            
            # Sauvegarder en base
            logs_config_db = LogsConfigDatabase()
            success = logs_config_db.save_guild_config(self.guild_id, config_data)
            
            if success:
                # Créer embed de confirmation
                embed = discord.Embed(
                    title="✅ Configuration des Logs Mise à Jour",
                    description="La configuration des logs a été sauvegardée avec succès !",
                    color=0xff6b35
                )
                
                embed.add_field(
                    name="📝 Canal Principal",
                    value=f"`{config_data['main_channel']}`",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Types Activés",
                    value=f"`{len(config_data['enabled_types'])}` types configurés",
                    inline=True
                )
                
                embed.add_field(
                    name="🎯 Canaux Spécialisés",
                    value=f"`{len(config_data['specialized_channels'])}` canaux configurés",
                    inline=True
                )
                
                embed.add_field(
                    name="🚫 Filtres",
                    value=f"`{len(config_data['filters'])}` filtres actifs",
                    inline=True
                )
                
                embed.add_field(
                    name="⚙️ Config Avancée",
                    value="✅ Configurée" if config_data['advanced'] else "❌ Non configurée",
                    inline=True
                )
                
                embed.add_field(
                    name="🕒 Mise à Jour",
                    value=f"<t:{int(datetime.now().timestamp())}:R>",
                    inline=True
                )
                
                embed.set_footer(text=f"Configuré par {interaction.user.display_name}")
                
                # Boutons d'action
                view = LogsConfigActionView(self.guild_id)
                
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors de la sauvegarde de la configuration.", 
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors du traitement : {str(e)}", 
                ephemeral=True
            )

class LogsConfigActionView(discord.ui.View):
    """Boutons d'action pour la configuration des logs"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.button(label="🔄 Tester Config", style=discord.ButtonStyle.primary, emoji="🧪")
    async def test_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Tester la configuration actuelle"""
        await interaction.response.defer(ephemeral=True)
        
        logs_config_db = LogsConfigDatabase()
        config = logs_config_db.get_guild_config(self.guild_id)
        
        if not config:
            await interaction.followup.send("❌ Aucune configuration trouvée.", ephemeral=True)
            return
        
        # Test des canaux
        guild = interaction.guild
        test_results = []
        
        # Test canal principal
        main_channel_id = config.get('main_channel', '').replace('<#', '').replace('>', '').replace('#', '')
        if main_channel_id.isdigit():
            channel = guild.get_channel(int(main_channel_id))
            if channel:
                test_results.append("✅ Canal principal accessible")
                # Essayer d'envoyer un message de test
                try:
                    test_embed = discord.Embed(
                        title="🧪 Test de Configuration Logs",
                        description="Ce message teste la configuration des logs.",
                        color=0x4caf50
                    )
                    await channel.send(embed=test_embed, delete_after=10)
                    test_results.append("✅ Envoi de message possible")
                except:
                    test_results.append("❌ Impossible d'envoyer des messages")
            else:
                test_results.append("❌ Canal principal introuvable")
        else:
            test_results.append("❌ ID de canal principal invalide")
        
        # Test canaux spécialisés
        specialized = config.get('specialized_channels', {})
        for log_type, channel_id in specialized.items():
            if channel_id.isdigit():
                channel = guild.get_channel(int(channel_id))
                if channel:
                    test_results.append(f"✅ Canal {log_type} accessible")
                else:
                    test_results.append(f"❌ Canal {log_type} introuvable")
        
        # Créer embed de résultat
        embed = discord.Embed(
            title="🧪 Résultats du Test de Configuration",
            description="\n".join(test_results),
            color=0x4caf50 if all("✅" in result for result in test_results) else 0xf44336
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, emoji="📈")
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Voir les statistiques des logs"""
        await interaction.response.defer(ephemeral=True)
        
        logs_config_db = LogsConfigDatabase()
        stats = logs_config_db.get_logs_statistics(self.guild_id)
        
        embed = discord.Embed(
            title="📊 Statistiques des Logs",
            color=0xff6b35
        )
        
        embed.add_field(
            name="📝 Logs Envoyés (24h)",
            value=f"`{stats.get('logs_24h', 0)}`",
            inline=True
        )
        
        embed.add_field(
            name="📈 Total Logs",
            value=f"`{stats.get('total_logs', 0)}`",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Types Actifs",
            value=f"`{stats.get('active_types', 0)}`",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Dernière Activité",
            value=f"<t:{int(stats.get('last_log_timestamp', datetime.now().timestamp()))}:R>",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🗑️ Réinitialiser", style=discord.ButtonStyle.danger, emoji="🔄")
    async def reset_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Réinitialiser la configuration"""
        embed = discord.Embed(
            title="⚠️ Confirmation de Réinitialisation",
            description="Êtes-vous sûr de vouloir réinitialiser toute la configuration des logs ?",
            color=0xf44336
        )
        
        view = discord.ui.View()
        
        async def confirm_reset(confirm_interaction):
            logs_config_db = LogsConfigDatabase()
            success = logs_config_db.reset_guild_config(self.guild_id)
            
            if success:
                await confirm_interaction.response.edit_message(
                    content="✅ Configuration réinitialisée avec succès !",
                    embed=None,
                    view=None
                )
            else:
                await confirm_interaction.response.edit_message(
                    content="❌ Erreur lors de la réinitialisation.",
                    embed=None,
                    view=None
                )
        
        confirm_button = discord.ui.Button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
        confirm_button.callback = confirm_reset
        
        cancel_button = discord.ui.Button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
        cancel_button.callback = lambda i: i.response.edit_message(content="Réinitialisation annulée.", embed=None, view=None)
        
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class LogsConfigDatabase:
    """Gestionnaire de base de données pour la configuration des logs"""
    
    def __init__(self, db_path="logs_config.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données des configurations de logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_logs_config (
                guild_id TEXT PRIMARY KEY,
                main_channel TEXT,
                enabled_types TEXT,
                specialized_channels TEXT,
                filters TEXT,
                advanced_config TEXT,
                created_at TEXT,
                updated_at TEXT,
                updated_by TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                log_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                channel_id TEXT,
                action_details TEXT,
                success BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_guild_config(self, guild_id: int, config_data: dict) -> bool:
        """Sauvegarder la configuration d'un serveur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO guild_logs_config 
                (guild_id, main_channel, enabled_types, specialized_channels, 
                 filters, advanced_config, created_at, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(guild_id),
                config_data.get('main_channel', ''),
                json.dumps(config_data.get('enabled_types', [])),
                json.dumps(config_data.get('specialized_channels', {})),
                json.dumps(config_data.get('filters', {})),
                json.dumps(config_data.get('advanced', {})),
                config_data.get('created_at', datetime.now().isoformat()),
                config_data.get('updated_at', datetime.now().isoformat()),
                config_data.get('updated_by', '')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur sauvegarde config logs: {e}")
            return False
    
    def get_guild_config(self, guild_id: int) -> dict:
        """Récupérer la configuration d'un serveur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT main_channel, enabled_types, specialized_channels, 
                   filters, advanced_config, updated_at, updated_by
            FROM guild_logs_config 
            WHERE guild_id = ? AND is_active = 1
        ''', (str(guild_id),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'main_channel': result[0],
                'enabled_types': json.loads(result[1] or '[]'),
                'specialized_channels': json.loads(result[2] or '{}'),
                'filters': json.loads(result[3] or '{}'),
                'advanced': json.loads(result[4] or '{}'),
                'updated_at': result[5],
                'updated_by': result[6]
            }
        return {}
    
    def log_event(self, guild_id: int, log_type: str, user_id: str = None, 
                  channel_id: str = None, details: str = None) -> bool:
        """Enregistrer un événement de log"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs_statistics 
                (guild_id, log_type, timestamp, user_id, channel_id, action_details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(guild_id), log_type, datetime.now().isoformat(),
                user_id, channel_id, details
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur log événement: {e}")
            return False
    
    def get_logs_statistics(self, guild_id: int) -> dict:
        """Récupérer les statistiques des logs d'un serveur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Logs des dernières 24h
        cursor.execute('''
            SELECT COUNT(*) FROM logs_statistics 
            WHERE guild_id = ? AND datetime(timestamp) > datetime('now', '-1 day')
        ''', (str(guild_id),))
        logs_24h = cursor.fetchone()[0]
        
        # Total des logs
        cursor.execute('''
            SELECT COUNT(*) FROM logs_statistics WHERE guild_id = ?
        ''', (str(guild_id),))
        total_logs = cursor.fetchone()[0]
        
        # Types actifs
        cursor.execute('''
            SELECT COUNT(DISTINCT log_type) FROM logs_statistics WHERE guild_id = ?
        ''', (str(guild_id),))
        active_types = cursor.fetchone()[0]
        
        # Dernier log
        cursor.execute('''
            SELECT MAX(timestamp) FROM logs_statistics WHERE guild_id = ?
        ''', (str(guild_id),))
        last_log = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'logs_24h': logs_24h,
            'total_logs': total_logs,
            'active_types': active_types,
            'last_log_timestamp': datetime.fromisoformat(last_log).timestamp() if last_log else datetime.now().timestamp()
        }
    
    def reset_guild_config(self, guild_id: int) -> bool:
        """Réinitialiser la configuration d'un serveur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE guild_logs_config SET is_active = 0 WHERE guild_id = ?
            ''', (str(guild_id),))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur reset config: {e}")
            return False

class LogsConfigCog(commands.Cog):
    """Cog pour la gestion de la configuration des logs"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logs_db = LogsConfigDatabase()
    
    @commands.slash_command(
        name="logs-config",
        description="🔧 Configurer le système de logs avancé (Admin uniquement)"
    )
    @commands.has_permissions(administrator=True)
    async def logs_config(self, ctx: discord.ApplicationContext):
        """Commande de configuration des logs"""
        
        # Récupérer la config actuelle
        current_config = self.logs_db.get_guild_config(ctx.guild.id)
        
        # Créer embed d'introduction  
        embed = discord.Embed(
            title="🔧 Configuration des Logs - Arsenal Bot",
            description="Configurez un système de logs avancé pour votre serveur.\n" +
                       "Style DraftBot mais avec plus de fonctionnalités !",
            color=0xff6b35
        )
        
        embed.add_field(
            name="📝 Canal Principal",
            value=current_config.get('main_channel', '❌ Non configuré'),
            inline=True
        )
        
        embed.add_field(
            name="📋 Types Activés",
            value=f"{len(current_config.get('enabled_types', []))} types",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Canaux Spécialisés",
            value=f"{len(current_config.get('specialized_channels', {}))} canaux",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Fonctionnalités Disponibles",
            value="• Logs de modération (ban, kick, warn)\n" +
                  "• Logs de messages (suppression, édition)\n" +
                  "• Logs vocaux (join, leave, mute)\n" +
                  "• Logs de rôles et permissions\n" +
                  "• Logs d'économie et Hunt Royal\n" +
                  "• Filtrage par utilisateur/rôle/canal\n" +
                  "• Canaux spécialisés par type\n" +
                  "• Configuration JSON avancée",
            inline=False
        )
        
        embed.set_footer(text=f"Serveur: {ctx.guild.name} • Configuré par: {ctx.author.display_name}")
        
        # Bouton pour ouvrir le modal
        view = discord.ui.View()
        
        async def open_config_modal(interaction):
            modal = LogsConfigModal(ctx.guild.id, current_config)
            await interaction.response.send_modal(modal)
        
        config_button = discord.ui.Button(
            label="🔧 Configurer",
            style=discord.ButtonStyle.primary,
            emoji="⚙️"
        )
        config_button.callback = open_config_modal
        
        view.add_item(config_button)
        
        await ctx.respond(embed=embed, view=view)

def setup(bot):
    """Ajouter le cog au bot"""
    bot.add_cog(LogsConfigCog(bot))
