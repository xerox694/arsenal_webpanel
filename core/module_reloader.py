"""
🔄 MODULE RELOADER - Système de Hot-Reload pour Arsenal Bot
==========================================================

Système permettant de recharger les modules à chaud sans redémarrer le bot
- Rechargement automatique lors de modifications
- Interface de commandes pour reload manuel
- Gestion des erreurs et rollback
- Support pour tous les modules Arsenal

Créé pour Arsenal Bot V4 - Hot Reload System
"""

import os
import sys
import importlib
import importlib.util
import traceback
import asyncio
import time
import re
from datetime import datetime
from pathlib import Path
import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, List, Optional
import json

# Commandes slash pour le rechargement de modules
reload_group = app_commands.Group(name="reload", description="🔄 Rechargement de modules à chaud")

@reload_group.command(name="module", description="Recharge un module Arsenal spécifique")
@app_commands.describe(module="Nom du module à recharger")
@app_commands.choices(module=[
    app_commands.Choice(name="🏹 Profils Utilisateurs", value="user_profiles_system"),
    app_commands.Choice(name="🛡️ AutoMod", value="automod_system"), 
    app_commands.Choice(name="💰 Économie", value="economy_system"),
    app_commands.Choice(name="🎫 Tickets", value="ticket_system"),
    app_commands.Choice(name="🎧 Voice Hub", value="voice_hub_system"),
    app_commands.Choice(name="🆘 Système d'Aide", value="help_system")
])
@app_commands.checks.has_permissions(administrator=True)
async def reload_module_slash(interaction: discord.Interaction, module: str):
    reloader_cog = interaction.client.get_cog('ReloaderCommands')
    if not reloader_cog:
        await interaction.response.send_message("❌ Système de rechargement non chargé", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Utiliser le système de rechargement Arsenal
    success, result_message = await reloader_cog.reloader.reload_arsenal_module(module)
    
    embed_color = discord.Color.green() if success else discord.Color.red()
    embed_title = "✅ Module rechargé" if success else "❌ Échec du rechargement"
    
    embed = discord.Embed(
        title=embed_title,
        description=result_message,
        color=embed_color
    )
    
    if success:
        embed.add_field(
            name="📋 Module", 
            value=f"**{module}**", 
            inline=True
        )
        embed.add_field(
            name="⏰ Heure",
            value=f"<t:{int(datetime.now().timestamp())}:T>",
            inline=True
        )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@reload_group.command(name="all", description="Recharge tous les modules Arsenal")
@app_commands.checks.has_permissions(administrator=True)
async def reload_all_slash(interaction: discord.Interaction):
    reloader_cog = interaction.client.get_cog('ReloaderCommands')
    if not reloader_cog:
        await interaction.response.send_message("❌ Système de rechargement non chargé", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    results = []
    total = len(reloader_cog.reloader.arsenal_modules)
    current = 0
    
    # Message de progression initial
    initial_embed = discord.Embed(
        title="🔄 Rechargement en masse",
        description=f"Démarrage du rechargement de {total} modules...",
        color=discord.Color.orange()
    )
    await interaction.followup.send(embed=initial_embed, ephemeral=True)
    
    for module_name in reloader_cog.reloader.arsenal_modules.keys():
        current += 1
        
        # Recharger le module
        success, result_msg = await reloader_cog.reloader.reload_arsenal_module(module_name)
        results.append({
            "module": module_name,
            "success": success,
            "message": result_msg
        })
        
        await asyncio.sleep(0.5)  # Petite pause
    
    # Résultats finaux
    successful = sum(1 for r in results if r["success"])
    failed = total - successful
    
    final_embed = discord.Embed(
        title="✅ Rechargement terminé",
        description=f"**Résultats:** {successful} réussis, {failed} échoués sur {total} modules",
        color=discord.Color.green() if failed == 0 else discord.Color.orange()
    )
    
    # Détails
    success_list = [f"✅ {r['module']}" for r in results if r["success"]]
    error_list = [f"❌ {r['module']}" for r in results if not r["success"]]
    
    if success_list:
        final_embed.add_field(
            name="✅ Succès",
            value="\n".join(success_list[:10]),  # Limiter pour éviter les embeds trop longs
            inline=True
        )
    
    if error_list:
        final_embed.add_field(
            name="❌ Erreurs", 
            value="\n".join(error_list[:10]),
            inline=True
        )
    
    await interaction.edit_original_response(embed=final_embed)

@reload_group.command(name="status", description="Affiche le statut des modules Arsenal")
async def reload_status_slash(interaction: discord.Interaction):
    reloader_cog = interaction.client.get_cog('ReloaderCommands')
    if not reloader_cog:
        await interaction.response.send_message("❌ Système de rechargement non chargé", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🔄 Statut des Modules Arsenal",
        description="État actuel des modules avec rechargement avancé",
        color=discord.Color.blue()
    )
    
    loaded_count = 0
    total_count = len(reloader_cog.reloader.arsenal_modules)
    
    for module_name, config in reloader_cog.reloader.arsenal_modules.items():
        # Vérifier si le Cog est chargé
        cog = interaction.client.get_cog(config["cog_class"])
        if cog:
            status = "✅ Chargé"
            loaded_count += 1
        else:
            status = "❌ Non chargé"
        
        embed.add_field(
            name=f"{status} **{module_name}**",
            value=f"Cog: `{config['cog_class']}`",
            inline=True
        )
    
    embed.add_field(
        name="📊 Résumé",
        value=f"**{loaded_count}/{total_count}** modules chargés",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

class ModuleReloader:
    """Gestionnaire de rechargement de modules"""
    
    def __init__(self, bot):
        self.bot = bot
        self.modules_info = {}
        self.watched_directories = [
            "modules/",
            "commands/", 
            "core/",
            "utils/"
        ]
        self.auto_reload = True
        self.reload_log = []
        
        # Modules Arsenal spéciaux avec rechargement avancé
        self.arsenal_modules = {
            "user_profiles_system": {
                "path": "modules.user_profiles_system",
                "cog_class": "UserProfileCog",
                "commands": ["profile_group"]
            },
            "automod_system": {
                "path": "modules.automod_system", 
                "cog_class": "AutoModCog",
                "commands": ["automod_group"]
            },
            "economy_system": {
                "path": "modules.economy_system",
                "cog_class": "EconomyCog", 
                "commands": ["economy_group"]
            },
            "ticket_system": {
                "path": "modules.ticket_system",
                "cog_class": "TicketCog",
                "commands": ["ticket_group"]
            },
            "voice_hub_system": {
                "path": "modules.voice_hub_system",
                "cog_class": "VoiceHubCog",
                "commands": []
            },
            "help_system": {
                "path": "commands.help_system",
                "cog_class": "HelpCog",
                "commands": ["help_group", "simple_help"]
            }
        }
        
    def scan_modules(self):
        """Scanner tous les modules disponibles"""
        modules = {}
        
        for directory in self.watched_directories:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if file.endswith('.py') and not file.startswith('__'):
                        module_name = file[:-3]  # Enlever .py
                        module_path = os.path.join(directory, file)
                        
                        modules[module_name] = {
                            "path": module_path,
                            "directory": directory,
                            "last_modified": os.path.getmtime(module_path),
                            "loaded": False,
                            "error": None
                        }
        
        self.modules_info = modules
        return modules
    
    async def load_module(self, module_name: str):
        """Charger un module spécifique"""
        if module_name not in self.modules_info:
            return False, f"Module {module_name} non trouvé"
        
        try:
            module_info = self.modules_info[module_name]
            module_path = module_info["path"]
            
            # Importer le module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            
            # Ajouter au cache des modules
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Si le module a une fonction setup, l'appeler
            if hasattr(module, 'setup'):
                await module.setup(self.bot)
            
            module_info["loaded"] = True
            module_info["error"] = None
            
            # Logger
            log_entry = {
                "action": "load",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            self.reload_log.append(log_entry)
            
            return True, f"Module {module_name} chargé avec succès"
            
        except Exception as e:
            error_msg = f"Erreur chargement {module_name}: {str(e)}"
            module_info["error"] = error_msg
            
            log_entry = {
                "action": "load",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            self.reload_log.append(log_entry)
            
            return False, error_msg
    
    async def reload_arsenal_module(self, module_name: str):
        """Recharger un module Arsenal spécifique (avec Cog)"""
        if module_name not in self.arsenal_modules:
            return False, f"Module Arsenal '{module_name}' non reconnu"
        
        try:
            module_config = self.arsenal_modules[module_name]
            module_path = module_config["path"]
            cog_class_name = module_config["cog_class"]
            commands_to_remove = module_config.get("commands", [])
            
            # Étape 1: Décharger l'ancien Cog s'il existe
            existing_cog = self.bot.get_cog(cog_class_name)
            if existing_cog:
                await self.bot.remove_cog(cog_class_name)
                print(f"🗑️ Ancien Cog {cog_class_name} déchargé")
            
            # Étape 2: Supprimer les commandes slash du tree
            for cmd_name in commands_to_remove:
                try:
                    # Trouver et supprimer la commande du tree
                    for command in self.bot.tree._global_commands.copy():
                        if hasattr(command, 'name') and command.name == cmd_name.replace('_group', ''):
                            self.bot.tree.remove_command(command.name)
                            print(f"🗑️ Commande slash '{command.name}' supprimée")
                except Exception as e:
                    print(f"⚠️ Erreur suppression commande {cmd_name}: {e}")
            
            # Étape 3: Recharger le module Python
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
                print(f"🔄 Module Python {module_path} rechargé")
            else:
                # Importer pour la première fois
                imported_module = importlib.import_module(module_path)
                print(f"📥 Module Python {module_path} importé")
            
            # Étape 4: Recharger le Cog
            reloaded_module = sys.modules[module_path]
            cog_class = getattr(reloaded_module, cog_class_name)
            new_cog = cog_class(self.bot)
            await self.bot.add_cog(new_cog)
            print(f"✅ Nouveau Cog {cog_class_name} chargé")
            
            # Étape 5: Ré-ajouter les commandes slash
            for cmd_name in commands_to_remove:
                try:
                    if hasattr(reloaded_module, cmd_name):
                        command_obj = getattr(reloaded_module, cmd_name)
                        self.bot.tree.add_command(command_obj)
                        print(f"✅ Commande slash '{cmd_name}' ré-ajoutée")
                except Exception as e:
                    print(f"⚠️ Erreur ajout commande {cmd_name}: {e}")
            
            # Étape 6: Synchroniser les commandes
            try:
                await self.bot.tree.sync()
                print("🔄 Commandes slash synchronisées")
            except Exception as e:
                print(f"⚠️ Erreur sync commandes: {e}")
            
            # Log
            log_entry = {
                "action": "reload_arsenal",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "details": f"Cog {cog_class_name} rechargé avec commandes"
            }
            self.reload_log.append(log_entry)
            
            return True, f"✅ Module Arsenal '{module_name}' rechargé avec succès!"
            
        except Exception as e:
            error_msg = f"❌ Erreur rechargement {module_name}: {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            
            log_entry = {
                "action": "reload_arsenal",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            self.reload_log.append(log_entry)
            
            return False, error_msg
        
    async def reload_module(self, module_name: str):
        """Recharger un module existant"""
        if module_name not in self.modules_info:
            return False, f"Module {module_name} non trouvé"
        
        try:
            module_info = self.modules_info[module_name]
            
            # Si le module est déjà chargé, le décharger d'abord
            if module_name in sys.modules:
                module = sys.modules[module_name]
                
                # Appeler teardown si disponible
                if hasattr(module, 'teardown'):
                    await module.teardown(self.bot)
                
                # Retirer du cache
                del sys.modules[module_name]
            
            # Recharger
            success, message = await self.load_module(module_name)
            
            if success:
                # Mettre à jour le timestamp
                module_info["last_modified"] = os.path.getmtime(module_info["path"])
                
                log_entry = {
                    "action": "reload",
                    "module": module_name,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
                self.reload_log.append(log_entry)
                
                return True, f"Module {module_name} rechargé avec succès"
            else:
                return False, message
                
        except Exception as e:
            error_msg = f"Erreur rechargement {module_name}: {str(e)}"
            
            log_entry = {
                "action": "reload",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            self.reload_log.append(log_entry)
            
            return False, error_msg
    
    async def unload_module(self, module_name: str):
        """Décharger un module"""
        if module_name not in sys.modules:
            return False, f"Module {module_name} non chargé"
        
        try:
            module = sys.modules[module_name]
            
            # Appeler teardown si disponible
            if hasattr(module, 'teardown'):
                await module.teardown(self.bot)
            
            # Retirer du cache
            del sys.modules[module_name]
            
            if module_name in self.modules_info:
                self.modules_info[module_name]["loaded"] = False
            
            log_entry = {
                "action": "unload",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            self.reload_log.append(log_entry)
            
            return True, f"Module {module_name} déchargé avec succès"
            
        except Exception as e:
            error_msg = f"Erreur déchargement {module_name}: {str(e)}"
            
            log_entry = {
                "action": "unload",
                "module": module_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            self.reload_log.append(log_entry)
            
            return False, error_msg
    
    async def check_for_changes(self):
        """Vérifier les modifications de fichiers"""
        changes = []
        
        for module_name, info in self.modules_info.items():
            try:
                current_modified = os.path.getmtime(info["path"])
                if current_modified > info["last_modified"]:
                    changes.append(module_name)
            except:
                pass
        
        return changes
    
    async def auto_reload_loop(self):
        """Boucle de rechargement automatique"""
        while self.auto_reload:
            try:
                changes = await self.check_for_changes()
                
                for module_name in changes:
                    if self.modules_info[module_name]["loaded"]:
                        success, message = await self.reload_module(module_name)
                        print(f"🔄 Auto-reload {module_name}: {message}")
                
                await asyncio.sleep(5)  # Vérifier toutes les 5 secondes
                
            except Exception as e:
                print(f"❌ Erreur auto-reload: {e}")
                await asyncio.sleep(10)

class ReloaderCommands(commands.Cog):
    """Commandes de gestion des modules"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reloader = ModuleReloader(bot)
        
        # Scanner les modules au démarrage
        self.reloader.scan_modules()
        
        # Démarrer la boucle auto-reload
        if self.reloader.auto_reload:
            asyncio.create_task(self.reloader.auto_reload_loop())
    
    @commands.group(name='module', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def module_management(self, ctx):
        """Commandes de gestion des modules"""
        embed = discord.Embed(
            title="🔄 Gestionnaire de Modules Arsenal",
            description="Système de rechargement à chaud des modules",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📋 Commandes",
            value="`!module list` - Lister tous les modules\n"
                  "`!module reload <nom>` - Recharger un module\n"
                  "`!module load <nom>` - Charger un module\n"
                  "`!module unload <nom>` - Décharger un module\n"
                  "`!module status` - État des modules\n"
                  "`!module logs` - Logs de rechargement",
            inline=False
        )
        
        embed.add_field(
            name="🏹 Modules Spéciaux",
            value="`!module reload hunt_royal_system` - Recharger Hunt Royal\n"
                  "`!module reload suggestions` - Recharger système suggestions\n"
                  "`!module scan` - Rescanner les modules",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='list')
    async def list_modules(self, ctx):
        """Lister tous les modules disponibles"""
        modules = self.reloader.modules_info
        
        embed = discord.Embed(
            title="📋 Modules Arsenal Disponibles",
            description=f"Total: {len(modules)} modules",
            color=0x0099ff
        )
        
        loaded_modules = []
        unloaded_modules = []
        error_modules = []
        
        for name, info in modules.items():
            status = "✅" if info["loaded"] else "⭕"
            if info["error"]:
                status = "❌"
                error_modules.append(f"{status} **{name}** - {info['error'][:50]}...")
            elif info["loaded"]:
                loaded_modules.append(f"{status} **{name}** - {info['directory']}")
            else:
                unloaded_modules.append(f"{status} **{name}** - {info['directory']}")
        
        if loaded_modules:
            embed.add_field(
                name="✅ Modules Chargés",
                value="\n".join(loaded_modules[:10]),  # Limiter à 10
                inline=False
            )
        
        if unloaded_modules:
            embed.add_field(
                name="⭕ Modules Non Chargés",
                value="\n".join(unloaded_modules[:10]),
                inline=False
            )
        
        if error_modules:
            embed.add_field(
                name="❌ Modules en Erreur",
                value="\n".join(error_modules[:5]),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='reload')
    async def reload_module(self, ctx, module_name: str):
        """Recharger un module spécifique"""
        # Message de chargement
        loading_embed = discord.Embed(
            title="🔄 Rechargement en cours...",
            description=f"Rechargement du module **{module_name}**",
            color=0xffa500
        )
        message = await ctx.send(embed=loading_embed)
        
        # Vérifier si c'est un module Arsenal spécial
        if module_name in self.reloader.arsenal_modules:
            success, result_message = await self.reloader.reload_arsenal_module(module_name)
        elif module_name in self.reloader.modules_info:
            success, result_message = await self.reloader.reload_module(module_name)
        else:
            success = False
            result_message = f"Module **{module_name}** non trouvé"
        
        # Résultat
        embed_color = 0x00ff00 if success else 0xff0000
        embed_title = "✅ Rechargement réussi" if success else "❌ Échec du rechargement"
        
        result_embed = discord.Embed(
            title=embed_title,
            description=result_message,
            color=embed_color
        )
        
        if success:
            result_embed.add_field(
                name="📋 Module",
                value=f"**{module_name}**",
                inline=True
            )
            result_embed.add_field(
                name="⏰ Heure",
                value=f"<t:{int(datetime.now().timestamp())}:T>",
                inline=True
            )
        
        await message.edit(embed=result_embed)
        
        # Recharger le module
        success, result_message = await self.reloader.reload_module(module_name)
        
        # Résultat
        embed = discord.Embed(
            title="✅ Rechargement réussi" if success else "❌ Échec du rechargement",
            description=result_message,
            color=0x00ff00 if success else 0xff0000
        )
        
        if success:
            embed.add_field(
                name="📊 Infos",
                value=f"**Module:** {module_name}\n"
                      f"**Timestamp:** {datetime.now().strftime('%H:%M:%S')}\n"
                      f"**Répertoire:** {self.reloader.modules_info[module_name]['directory']}",
                inline=False
            )
        
        await message.edit(embed=embed)
    
    @module_management.command(name='load')
    async def load_module(self, ctx, module_name: str):
        """Charger un module"""
        success, message = await self.reloader.load_module(module_name)
        
        embed = discord.Embed(
            title="✅ Module chargé" if success else "❌ Échec du chargement",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='unload')
    async def unload_module(self, ctx, module_name: str):
        """Décharger un module"""
        success, message = await self.reloader.unload_module(module_name)
        
        embed = discord.Embed(
            title="✅ Module déchargé" if success else "❌ Échec du déchargement",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='status')
    async def module_status(self, ctx):
        """État détaillé des modules"""
        modules = self.reloader.modules_info
        
        total = len(modules)
        loaded = sum(1 for m in modules.values() if m["loaded"])
        errors = sum(1 for m in modules.values() if m["error"])
        
        embed = discord.Embed(
            title="📊 État des Modules Arsenal",
            description=f"**Total:** {total} | **Chargés:** {loaded} | **Erreurs:** {errors}",
            color=0x00ff00 if errors == 0 else 0xffa500
        )
        
        # Statistiques
        embed.add_field(
            name="📈 Statistiques",
            value=f"**Taux de chargement:** {(loaded/total*100):.1f}%\n"
                  f"**Auto-reload:** {'✅ Actif' if self.reloader.auto_reload else '❌ Inactif'}\n"
                  f"**Dernière vérification:** {datetime.now().strftime('%H:%M:%S')}",
            inline=True
        )
        
        # Répertoires surveillés
        directories = "\n".join([f"• {d}" for d in self.reloader.watched_directories])
        embed.add_field(
            name="📁 Répertoires Surveillés",
            value=directories,
            inline=True
        )
        
        # Modules critiques
        critical_modules = ["hunt_royal_system", "suggestions", "music_system"]
        critical_status = []
        
        for module in critical_modules:
            if module in modules:
                status = "✅" if modules[module]["loaded"] else "❌"
                critical_status.append(f"{status} {module}")
        
        if critical_status:
            embed.add_field(
                name="🔥 Modules Critiques",
                value="\n".join(critical_status),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='arsenal')
    async def arsenal_modules(self, ctx):
        """Affiche les modules Arsenal spéciaux"""
        embed = discord.Embed(
            title="🏹 Modules Arsenal Spéciaux",
            description="Modules avec rechargement avancé (Cogs + Commandes)",
            color=0x7289da
        )
        
        for module_name, config in self.reloader.arsenal_modules.items():
            # Vérifier si le Cog est chargé
            cog = self.bot.get_cog(config["cog_class"])
            status = "✅ Chargé" if cog else "❌ Non chargé"
            
            embed.add_field(
                name=f"{status} **{module_name}**",
                value=f"**Fichier:** `{config['path']}`\n"
                      f"**Cog:** `{config['cog_class']}`\n"
                      f"**Commandes:** {len(config.get('commands', []))}",
                inline=True
            )
        
        embed.add_field(
            name="🔄 Commandes",
            value="`!module reload <nom>` - Recharger un module Arsenal\n"
                  "`!module reload_all` - Recharger tous les modules\n"
                  "`!module arsenal` - Voir cette liste",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='reload_all')
    async def reload_all_arsenal(self, ctx):
        """Recharge tous les modules Arsenal"""
        embed = discord.Embed(
            title="🔄 Rechargement de tous les modules Arsenal",
            description="Démarrage du rechargement en masse...",
            color=0xffa500
        )
        message = await ctx.send(embed=embed)
        
        results = []
        total = len(self.reloader.arsenal_modules)
        current = 0
        
        for module_name in self.reloader.arsenal_modules.keys():
            current += 1
            
            # Mettre à jour le message de progression
            progress_embed = discord.Embed(
                title="🔄 Rechargement en cours...",
                description=f"Module: **{module_name}** ({current}/{total})",
                color=0xffa500
            )
            await message.edit(embed=progress_embed)
            
            # Recharger le module
            success, result_msg = await self.reloader.reload_arsenal_module(module_name)
            results.append({
                "module": module_name,
                "success": success,
                "message": result_msg
            })
            
            await asyncio.sleep(1)  # Petite pause entre les modules
        
        # Afficher les résultats
        successful = sum(1 for r in results if r["success"])
        failed = total - successful
        
        final_embed = discord.Embed(
            title="✅ Rechargement terminé",
            description=f"**Résultats:** {successful} réussis, {failed} échoués",
            color=0x00ff00 if failed == 0 else 0xffa500
        )
        
        # Détails des résultats
        success_list = []
        error_list = []
        
        for result in results:
            if result["success"]:
                success_list.append(f"✅ {result['module']}")
            else:
                error_list.append(f"❌ {result['module']}: {result['message'][:50]}...")
        
        if success_list:
            final_embed.add_field(
                name="✅ Succès",
                value="\n".join(success_list),
                inline=True
            )
        
        if error_list:
            final_embed.add_field(
                name="❌ Erreurs",
                value="\n".join(error_list),
                inline=True
            )
        
        await message.edit(embed=final_embed)
    
    @module_management.command(name='logs')
    async def module_logs(self, ctx, limit: int = 10):
        """Afficher les logs de rechargement"""
        logs = self.reloader.reload_log[-limit:]
        
        if not logs:
            embed = discord.Embed(
                title="📋 Logs de Rechargement",
                description="Aucun log disponible",
                color=0x999999
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Logs de Rechargement",
            description=f"Dernières {len(logs)} opérations",
            color=0x0099ff
        )
        
        for log in logs:
            status_icon = "✅" if log["success"] else "❌"
            timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
            
            value = f"**Action:** {log['action']}\n"
            value += f"**Timestamp:** {timestamp}\n"
            if not log["success"] and "error" in log:
                value += f"**Erreur:** {log['error'][:100]}..."
            
            embed.add_field(
                name=f"{status_icon} {log['module']}",
                value=value,
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @module_management.command(name='scan')
    async def scan_modules(self, ctx):
        """Rescanner les modules disponibles"""
        old_count = len(self.reloader.modules_info)
        modules = self.reloader.scan_modules()
        new_count = len(modules)
        
        embed = discord.Embed(
            title="🔍 Scan des Modules Terminé",
            description=f"**Avant:** {old_count} modules\n**Après:** {new_count} modules",
            color=0x00ff00
        )
        
        if new_count > old_count:
            embed.add_field(
                name="➕ Nouveaux Modules Détectés",
                value=f"+{new_count - old_count} modules trouvés",
                inline=False
            )
        
        # Lister les répertoires scannés
        scanned = []
        for directory in self.reloader.watched_directories:
            if os.path.exists(directory):
                count = len([f for f in os.listdir(directory) if f.endswith('.py')])
                scanned.append(f"• {directory}: {count} fichiers")
        
        embed.add_field(
            name="📁 Répertoires Scannés",
            value="\n".join(scanned),
            inline=False
        )
        
        await ctx.send(embed=embed)

# ==================== FONCTIONS D'INITIALISATION ====================

def setup(bot):
    """Charger le système de rechargement"""
    bot.add_cog(ReloaderCommands(bot))
    print("🔄 Système de rechargement de modules chargé !")

def teardown(bot):
    """Décharger le système de rechargement"""
    # Arrêter l'auto-reload
    for cog in bot.cogs.values():
        if hasattr(cog, 'reloader'):
            cog.reloader.auto_reload = False
    
    bot.remove_cog('ReloaderCommands')
    print("🔄 Système de rechargement déchargé")

if __name__ == "__main__":
    print("🔄 Module Reloader - Système de Hot-Reload initialisé")
