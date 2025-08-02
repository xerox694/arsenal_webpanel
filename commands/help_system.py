#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🆘 ARSENAL V4 - SYSTÈME D'AIDE COMPLET
Guide utilisateur pour toutes les fonctionnalités du bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Dict, List
from core.logger import log

class HelpSystem:
    """Système d'aide complet pour Arsenal V4"""
    
    def __init__(self):
        self.commands_data = {
            "admin": {
                "emoji": "👑",
                "title": "Administration",
                "description": "Commandes de gestion du serveur et configuration",
                "permission": "Administrateur",
                "commands": {
                    "/admin setup_welcome": "Configuration des messages de bienvenue",
                    "/admin test_welcome": "Tester le système de bienvenue",
                    "/admin setup_logs": "Configuration des salons de logs",
                    "/admin setup_roles": "Gestion automatique des rôles",
                    "/admin backup": "Sauvegarde complète du serveur",
                    "/admin restore": "Restauration depuis une sauvegarde",
                    "/admin maintenance": "Mode maintenance du bot",
                    "/admin stats": "Statistiques détaillées du serveur"
                }
            },
            "moderation": {
                "emoji": "🛡️", 
                "title": "Modération",
                "description": "Outils de modération et maintien de l'ordre",
                "permission": "Modérateur",
                "commands": {
                    "/mod kick": "Expulser un membre du serveur",
                    "/mod ban": "Bannir un membre définitivement",
                    "/mod tempban": "Bannissement temporaire",
                    "/mod mute": "Rendre muet temporairement",
                    "/mod unmute": "Retirer le mute d'un membre",
                    "/mod warn": "Donner un avertissement",
                    "/mod clear": "Supprimer des messages en masse",
                    "/mod slowmode": "Activer le mode lent",
                    "/mod lock": "Verrouiller un salon",
                    "/mod unlock": "Déverrouiller un salon"
                }
            },
            "automod": {
                "emoji": "🤖",
                "title": "Auto-Modération",
                "description": "Système automatique de modération avancé",
                "permission": "Administrateur",
                "commands": {
                    "/automod status": "Statut du système automod",
                    "/automod toggle": "Activer/désactiver l'automod",
                    "/automod config": "Configurer les paramètres",
                    "/automod add_word": "Ajouter un mot interdit",
                    "/automod remove_word": "Retirer un mot du filtre",
                    "/automod warnings": "Voir les avertissements",
                    "/automod clear_warnings": "Effacer les avertissements",
                    "/automod set_log_channel": "Définir le salon de logs",
                    "/automod detect_competitors": "Détecter les bots concurrents",
                    "/automod check_welcome": "Vérifier les bots de bienvenue",
                    "/automod disable_welcome_bots": "Guide désactivation bots"
                }
            },
            "tickets": {
                "emoji": "🎫",
                "title": "Système de Tickets",
                "description": "Gestion des demandes d'aide et support",
                "permission": "Modérateur",
                "commands": {
                    "/ticket setup": "Configurer le système de tickets",
                    "/ticket panel": "Créer le panel de tickets",
                    "/ticket close": "Fermer un ticket",
                    "/ticket add": "Ajouter quelqu'un au ticket",
                    "/ticket remove": "Retirer quelqu'un du ticket",
                    "/ticket transcript": "Créer un transcript",
                    "/ticket stats": "Statistiques des tickets",
                    "/ticket config": "Configuration avancée"
                }
            },
            "voice": {
                "emoji": "🎧",
                "title": "Hubs Vocaux",
                "description": "Salons vocaux temporaires et hubs",
                "permission": "Modérateur",
                "commands": {
                    "/hub create": "Créer un hub vocal",
                    "/hub delete": "Supprimer un hub",
                    "/hub config": "Configurer un hub",
                    "/hub list": "Liste des hubs actifs",
                    "/voice lock": "Verrouiller son salon temporaire",
                    "/voice unlock": "Déverrouiller son salon",
                    "/voice limit": "Limiter le nombre d'utilisateurs",
                    "/voice name": "Renommer son salon temporaire",
                    "/voice invite": "Inviter quelqu'un dans son salon",
                    "/voice kick": "Expulser quelqu'un de son salon"
                }
            },
            "economy": {
                "emoji": "💰",
                "title": "Économie & Nivellement",
                "description": "Système d'argent, d'expérience et de boutique",
                "permission": "Tous",
                "commands": {
                    "/economy balance": "Voir votre argent et niveau",
                    "/economy daily": "Récompense quotidienne",
                    "/economy work": "Travailler pour gagner de l'argent",
                    "/economy crime": "Commettre un crime (risqué)",
                    "/economy bank": "Gérer votre compte bancaire",
                    "/economy shop": "Voir la boutique premium",
                    "/economy buy": "Acheter un item de la boutique",
                    "/economy inventory": "Votre inventaire et boosts",
                    "/economy leaderboard": "Classement du serveur",
                    "/economy give": "Donner de l'argent à quelqu'un"
                }
            },
            "sanctions": {
                "emoji": "⚖️",
                "title": "Sanctions",
                "description": "Gestion des sanctions et historiques",
                "permission": "Modérateur", 
                "commands": {
                    "/sanction add": "Ajouter une sanction manuelle",
                    "/sanction remove": "Retirer une sanction",
                    "/sanction list": "Historique des sanctions",
                    "/sanction search": "Rechercher des sanctions",
                    "/sanction export": "Exporter l'historique",
                    "/sanction stats": "Statistiques des sanctions"
                }
            },
            "community": {
                "emoji": "👥",
                "title": "Communauté",
                "description": "Commandes pour tous les membres",
                "permission": "Tous",
                "commands": {
                    "/info": "Informations sur le bot",
                    "/avatar": "Afficher l'avatar d'un membre",
                    "/poll": "Créer un sondage",
                    "/vote": "Voter sur une proposition",
                    "/magic_8ball": "Boule magique 8",
                    "/spin_wheel": "Roue de la fortune",
                    "/top_vocal": "Top des utilisateurs vocaux",
                    "/top_messages": "Top des messages",
                    "/leaderboard": "Classement général",
                    "/random_quote": "Citation aléatoire",
                    "/signaler_bug": "Signaler un bug",
                    "/version": "Version du bot"
                }
            },
            "hunt_royal": {
                "emoji": "🏹",
                "title": "Hunt Royal",
                "description": "Système de jeu Hunt Royal intégré",
                "permission": "Tous",
                "commands": {
                    "/hunt stats": "Voir ses statistiques Hunt Royal",
                    "/hunt awaken": "Réveiller sa classe",
                    "/hunt list": "Liste des chasseurs actifs",
                    "/hunt update": "Mettre à jour son profil",
                    "/hunt cache": "Gestion du cache",
                    "/hunt hunter": "Informations chasseur",
                    "/hunt dungeon": "Système de donjons",
                    "/hunt suggest": "Suggérer une amélioration",
                    "/hunt economy": "Économie Hunt Royal",
                    "/hunt reload": "Recharger le système"
                }
            },
            "creator": {
                "emoji": "🔧",
                "title": "Créateur",
                "description": "Outils réservés au créateur du bot",
                "permission": "Créateur uniquement",
                "commands": {
                    "/creator shutdown": "Arrêter le bot",
                    "/creator restart": "Redémarrer le bot", 
                    "/creator eval": "Exécuter du code Python",
                    "/creator sql": "Exécuter des requêtes SQL",
                    "/creator backup_db": "Sauvegarder les bases de données",
                    "/creator system_info": "Informations système",
                    "/creator logs": "Consulter les logs",
                    "/creator update": "Mise à jour du bot"
                }
            }
        }
        
        self.quick_start_guide = [
            "1️⃣ **Configuration initiale** - Utilisez `/admin setup_welcome` et `/admin setup_logs`",
            "2️⃣ **Sécurité** - Activez l'automod avec `/automod toggle` et configurez avec `/automod config`",
            "3️⃣ **Support** - Créez le système de tickets avec `/ticket setup`",
            "4️⃣ **Vocal** - Configurez des hubs vocaux avec `/hub create`",
            "5️⃣ **Test** - Testez vos configurations avec les commandes de test"
        ]
        
        self.common_issues = {
            "Le bot ne répond pas": "Vérifiez les permissions du bot et qu'il est en ligne",
            "Messages de bienvenue en double": "Utilisez `/automod check_welcome` pour détecter les conflits",
            "Automod trop strict": "Ajustez avec `/automod config` et exemptez certains rôles",
            "Tickets ne fonctionnent pas": "Vérifiez les permissions avec `/ticket setup`",
            "Hubs vocaux ne se créent pas": "Vérifiez les permissions vocal du bot"
        }

# Commandes d'aide
help_group = app_commands.Group(name="help", description="🆘 Système d'aide Arsenal V4")

@help_group.command(name="menu", description="🗂️ Menu principal d'aide")
async def help_menu(interaction: discord.Interaction):
    """Menu principal d'aide avec toutes les catégories"""
    
    help_system = HelpSystem()
    
    embed = discord.Embed(
        title="🆘 Arsenal V4 - Guide Complet",
        description="**Sélectionnez une catégorie pour voir les commandes disponibles**",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Catégories Disponibles",
        value="\n".join([
            f"• `/help {category}` - {data['emoji']} {data['title']}"
            for category, data in help_system.commands_data.items()
        ]),
        inline=False
    )
    
    embed.add_field(
        name="🚀 Démarrage Rapide",
        value="Utilisez `/help quickstart` pour un guide de configuration rapide",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Dépannage",
        value="Utilisez `/help troubleshoot` pour résoudre les problèmes courants",
        inline=False
    )
    
    embed.add_field(
        name="📞 Support",
        value="Utilisez `/signaler_bug` pour signaler un problème ou `/help contact` pour nous contacter",
        inline=False
    )
    
    embed.set_footer(text="Arsenal V4 • Système d'aide avancé")
    embed.set_thumbnail(url=interaction.client.user.avatar.url if interaction.client.user.avatar else None)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@help_group.command(name="admin", description="👑 Aide pour les commandes d'administration")
async def help_admin(interaction: discord.Interaction):
    await _send_category_help(interaction, "admin")

@help_group.command(name="moderation", description="🛡️ Aide pour les commandes de modération")
async def help_moderation(interaction: discord.Interaction):
    await _send_category_help(interaction, "moderation")

@help_group.command(name="automod", description="🤖 Aide pour l'auto-modération")
async def help_automod(interaction: discord.Interaction):
    await _send_category_help(interaction, "automod")

@help_group.command(name="tickets", description="🎫 Aide pour le système de tickets")
async def help_tickets(interaction: discord.Interaction):
    await _send_category_help(interaction, "tickets")

@help_group.command(name="voice", description="🎧 Aide pour les hubs vocaux")
async def help_voice(interaction: discord.Interaction):
    await _send_category_help(interaction, "voice")

@help_group.command(name="sanctions", description="⚖️ Aide pour le système de sanctions")
async def help_sanctions(interaction: discord.Interaction):
    await _send_category_help(interaction, "sanctions")

@help_group.command(name="community", description="👥 Aide pour les commandes communautaires")
async def help_community(interaction: discord.Interaction):
    await _send_category_help(interaction, "community")

@help_group.command(name="hunt", description="🏹 Aide pour Hunt Royal")
async def help_hunt(interaction: discord.Interaction):
    await _send_category_help(interaction, "hunt_royal")

@help_group.command(name="creator", description="🔧 Aide pour les outils créateur")
async def help_creator(interaction: discord.Interaction):
    await _send_category_help(interaction, "creator")

async def _send_category_help(interaction: discord.Interaction, category: str):
    """Envoie l'aide pour une catégorie spécifique"""
    
    help_system = HelpSystem()
    
    if category not in help_system.commands_data:
        await interaction.response.send_message("❌ Catégorie introuvable", ephemeral=True)
        return
    
    data = help_system.commands_data[category]
    
    embed = discord.Embed(
        title=f"{data['emoji']} {data['title']} - Arsenal V4",
        description=f"**{data['description']}**\n**Permissions requises:** {data['permission']}",
        color=discord.Color.green()
    )
    
    # Diviser les commandes en chunks pour éviter la limite des embeds
    commands_list = list(data['commands'].items())
    chunks = [commands_list[i:i+10] for i in range(0, len(commands_list), 10)]
    
    for i, chunk in enumerate(chunks):
        field_name = "📝 Commandes Disponibles" if i == 0 else f"📝 Commandes (suite {i+1})"
        field_value = "\n".join([f"• `{cmd}` - {desc}" for cmd, desc in chunk])
        embed.add_field(name=field_name, value=field_value, inline=False)
    
    # Ajout d'exemples pratiques selon la catégorie
    if category == "admin":
        embed.add_field(
            name="💡 Configuration Recommandée",
            value="1. `/admin setup_welcome` → Configuration bienvenue\n2. `/admin setup_logs` → Logs système\n3. `/admin setup_roles` → Rôles automatiques",
            inline=False
        )
    elif category == "automod":
        embed.add_field(
            name="⚙️ Configuration Suggérée",
            value="1. `/automod toggle` → Activer le système\n2. `/automod config spam_detection enabled true` → Anti-spam\n3. `/automod set_log_channel` → Logs automod",
            inline=False
        )
    elif category == "tickets":
        embed.add_field(
            name="🎯 Mise en Place",
            value="1. `/ticket setup` → Configuration initiale\n2. `/ticket panel` → Créer le panel\n3. `/ticket config` → Personnalisation",
            inline=False
        )
    
    embed.set_footer(text=f"Arsenal V4 • Aide {data['title']}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@help_group.command(name="quickstart", description="🚀 Guide de démarrage rapide")
async def help_quickstart(interaction: discord.Interaction):
    """Guide de démarrage rapide pour configurer Arsenal"""
    
    help_system = HelpSystem()
    
    embed = discord.Embed(
        title="🚀 Guide de Démarrage Rapide - Arsenal V4",
        description="**Configuration essentielle en 5 étapes**",
        color=discord.Color.gold()
    )
    
    steps_text = "\n".join(help_system.quick_start_guide)
    embed.add_field(name="📋 Étapes de Configuration", value=steps_text, inline=False)
    
    embed.add_field(
        name="⚡ Configuration Express",
        value="```\n/admin setup_welcome\n/admin setup_logs\n/automod toggle\n/ticket setup\n/hub create```",
        inline=False
    )
    
    embed.add_field(
        name="🔍 Vérifications",
        value="• `/admin test_welcome` - Tester la bienvenue\n• `/automod status` - Vérifier l'automod\n• `/ticket stats` - État des tickets",
        inline=False
    )
    
    embed.add_field(
        name="❓ Besoin d'aide ?",
        value="Utilisez `/help [catégorie]` pour plus de détails sur chaque système",
        inline=False
    )
    
    embed.set_footer(text="Arsenal V4 • Configuration Rapide")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@help_group.command(name="troubleshoot", description="🔧 Résolution des problèmes courants")
async def help_troubleshoot(interaction: discord.Interaction):
    """Guide de dépannage pour les problèmes courants"""
    
    help_system = HelpSystem()
    
    embed = discord.Embed(
        title="🔧 Dépannage Arsenal V4",
        description="**Solutions aux problèmes les plus fréquents**",
        color=discord.Color.orange()
    )
    
    for issue, solution in help_system.common_issues.items():
        embed.add_field(
            name=f"❓ {issue}",
            value=f"💡 {solution}",
            inline=False
        )
    
    embed.add_field(
        name="🛠️ Diagnostics Utiles",
        value="• `/info` - État général du bot\n• `/admin stats` - Statistiques serveur\n• `/automod status` - État automod\n• `/ticket stats` - État tickets",
        inline=False
    )
    
    embed.add_field(
        name="📞 Support Avancé",
        value="Si le problème persiste:\n• `/signaler_bug` - Signaler le problème\n• Contactez l'équipe Arsenal\n• Vérifiez les permissions du bot",
        inline=False
    )
    
    embed.set_footer(text="Arsenal V4 • Assistance Technique")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@help_group.command(name="permissions", description="🔐 Guide des permissions nécessaires")
async def help_permissions(interaction: discord.Interaction):
    """Guide détaillé des permissions requises"""
    
    embed = discord.Embed(
        title="🔐 Permissions Arsenal V4",
        description="**Permissions nécessaires pour chaque fonctionnalité**",
        color=discord.Color.purple()
    )
    
    permissions_data = {
        "🤖 Permissions Bot Essentielles": [
            "✅ Lire les messages",
            "✅ Envoyer des messages", 
            "✅ Intégrer des liens",
            "✅ Joindre des fichiers",
            "✅ Lire l'historique des messages",
            "✅ Utiliser les emojis externes",
            "✅ Ajouter des réactions"
        ],
        "🛡️ Modération": [
            "✅ Gérer les messages",
            "✅ Expulser des membres",
            "✅ Bannir des membres",
            "✅ Exclure temporairement des membres",
            "✅ Gérer les rôles",
            "✅ Gérer les pseudos"
        ],
        "🎧 Vocal": [
            "✅ Se connecter aux salons vocaux",
            "✅ Parler dans les salons vocaux",
            "✅ Gérer les salons vocaux",
            "✅ Déplacer des membres",
            "✅ Rendre muet des membres",
            "✅ Rendre sourd des membres"
        ],
        "🎫 Tickets & Salons": [
            "✅ Gérer les salons",
            "✅ Gérer les permissions",
            "✅ Créer des invitations",
            "✅ Voir les salons vocaux"
        ]
    }
    
    for category, perms in permissions_data.items():
        embed.add_field(
            name=category,
            value="\n".join(perms),
            inline=True
        )
    
    embed.add_field(
        name="⚠️ Important",
        value="• Le bot doit avoir un rôle au-dessus des rôles qu'il gère\n• Certaines commandes nécessitent des permissions administrateur\n• Vérifiez les permissions par salon si nécessaire",
        inline=False
    )
    
    embed.set_footer(text="Arsenal V4 • Configuration Permissions")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@help_group.command(name="contact", description="📞 Informations de contact et support")
async def help_contact(interaction: discord.Interaction):
    """Informations de contact et support"""
    
    embed = discord.Embed(
        title="📞 Support Arsenal V4",
        description="**Besoin d'aide ? Contactez-nous !**",
        color=discord.Color.blurple()
    )
    
    embed.add_field(
        name="🐛 Signaler un Bug",
        value="Utilisez `/signaler_bug` directement dans Discord",
        inline=False
    )
    
    embed.add_field(
        name="💡 Suggestions",
        value="Utilisez les commandes de suggestion intégrées au bot",
        inline=False
    )
    
    embed.add_field(
        name="📚 Documentation",
        value="• `/help menu` - Guide complet\n• `/help quickstart` - Démarrage rapide\n• `/help troubleshoot` - Dépannage",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Informations Bot",
        value="• `/info` - Informations générales\n• `/version` - Version actuelle\n• `/admin stats` - Statistiques",
        inline=False
    )
    
    embed.add_field(
        name="🔄 Mises à Jour",
        value="Arsenal V4 est mis à jour régulièrement avec de nouvelles fonctionnalités et corrections",
        inline=False
    )
    
    embed.set_footer(text="Arsenal V4 • Équipe de Support")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@help_group.command(name="search", description="🔍 Rechercher une commande spécifique")
@app_commands.describe(query="Rechercher une commande ou fonctionnalité")
async def help_search(interaction: discord.Interaction, query: str):
    """Recherche dans les commandes disponibles"""
    
    help_system = HelpSystem()
    query_lower = query.lower()
    results = []
    
    # Recherche dans toutes les catégories
    for category, data in help_system.commands_data.items():
        # Recherche dans le titre et description
        if query_lower in data['title'].lower() or query_lower in data['description'].lower():
            results.append(f"**{data['emoji']} {data['title']}** - `/help {category}`")
        
        # Recherche dans les commandes
        for command, description in data['commands'].items():
            if query_lower in command.lower() or query_lower in description.lower():
                results.append(f"`{command}` - {description}")
    
    if not results:
        embed = discord.Embed(
            title="🔍 Recherche Arsenal V4",
            description=f"❌ Aucun résultat trouvé pour: **{query}**",
            color=discord.Color.red()
        )
        embed.add_field(
            name="💡 Suggestions",
            value="• Utilisez `/help menu` pour voir toutes les catégories\n• Essayez des mots-clés comme 'mod', 'admin', 'ticket'\n• Vérifiez l'orthographe",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="🔍 Résultats de Recherche",
            description=f"**Recherche pour:** {query}\n**{len(results)} résultat(s) trouvé(s)**",
            color=discord.Color.green()
        )
        
        # Limiter les résultats pour éviter la limite des embeds
        displayed_results = results[:15]
        if len(results) > 15:
            displayed_results.append(f"... et {len(results) - 15} autres résultats")
        
        embed.add_field(
            name="📝 Résultats",
            value="\n".join(displayed_results),
            inline=False
        )
    
    embed.set_footer(text="Arsenal V4 • Recherche Commandes")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Commande help simple aussi
@app_commands.command(name="aide", description="🆘 Aide rapide Arsenal V4")
@app_commands.describe(category="Catégorie d'aide spécifique (optionnel)")
@app_commands.choices(category=[
    app_commands.Choice(name="👑 Administration", value="admin"),
    app_commands.Choice(name="🛡️ Modération", value="moderation"),
    app_commands.Choice(name="🤖 Auto-Modération", value="automod"),
    app_commands.Choice(name="🎫 Tickets", value="tickets"),
    app_commands.Choice(name="🎧 Vocal", value="voice"),
    app_commands.Choice(name="👥 Communauté", value="community"),
    app_commands.Choice(name="🏹 Hunt Royal", value="hunt"),
    app_commands.Choice(name="🚀 Démarrage Rapide", value="quickstart"),
    app_commands.Choice(name="🔧 Dépannage", value="troubleshoot")
])
async def simple_help(interaction: discord.Interaction, category: Optional[str] = None):
    """Commande d'aide simple avec redirection vers le système complet"""
    
    if not category:
        # Rediriger vers le menu principal
        await help_menu(interaction)
    elif category == "quickstart":
        await help_quickstart(interaction)
    elif category == "troubleshoot": 
        await help_troubleshoot(interaction)
    else:
        await _send_category_help(interaction, category)

class HelpCog(commands.Cog):
    """Cog pour le système d'aide"""
    
    def __init__(self, bot):
        self.bot = bot
        log.info("🆘 Système d'aide initialisé")

async def setup(bot):
    """Setup du cog d'aide"""
    await bot.add_cog(HelpCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(help_group)
    bot.tree.add_command(simple_help)
    
    log.info("🆘 Système d'aide chargé avec succès")
