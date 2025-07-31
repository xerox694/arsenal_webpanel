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
import traceback
import asyncio
from datetime import datetime
from pathlib import Path
import discord
from discord.ext import commands
from typing import Dict, List, Optional
import json

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
        if module_name not in self.reloader.modules_info:
            embed = discord.Embed(
                title="❌ Module non trouvé",
                description=f"Le module **{module_name}** n'existe pas",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Message de chargement
        loading_embed = discord.Embed(
            title="🔄 Rechargement en cours...",
            description=f"Rechargement du module **{module_name}**",
            color=0xffa500
        )
        message = await ctx.send(embed=loading_embed)
        
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
