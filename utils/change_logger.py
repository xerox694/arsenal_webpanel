"""
📝 Arsenal V4 - Système de Logging des Changements
Enregistrement automatique de tous les changements pour les changelogs
Developed by XeRoX Elite © 2024-2025
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any

class ArsenalChangeLogger:
    def __init__(self, log_file="logs/changelog.json"):
        self.log_file = log_file
        self.changes = []
        self.session_id = f"session_{int(time.time())}"
        self.ensure_log_directory()
        self.load_existing_logs()
        
    def ensure_log_directory(self):
        """Créer le dossier logs s'il n'existe pas"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def load_existing_logs(self):
        """Charger les logs existants"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.changes = json.load(f)
            print(f"✅ Logs chargés: {len(self.changes)} entrées existantes")
        except Exception as e:
            print(f"⚠️ Erreur chargement logs: {e}")
            self.changes = []
            
    def save_logs(self):
        """Sauvegarder les logs"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.changes, f, indent=2, ensure_ascii=False)
            print(f"💾 Logs sauvegardés: {len(self.changes)} entrées")
        except Exception as e:
            print(f"❌ Erreur sauvegarde logs: {e}")
            
    def log_change(self, 
                   change_type: str, 
                   component: str, 
                   description: str, 
                   details: Dict = None,
                   impact: str = "normal",
                   version: str = "V4.2.1"):
        """Enregistrer un changement"""
        
        change_entry = {
            "id": f"change_{int(time.time())}_{len(self.changes)}",
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "session_id": self.session_id,
            "change_type": change_type,  # feature, bugfix, improvement, security, etc.
            "component": component,      # webpanel, bot, gui, api, database, etc.
            "description": description,
            "details": details or {},
            "impact": impact,           # low, normal, high, critical
            "version": version,
            "author": "XeRoX Elite",
            "category": self._categorize_change(change_type, component)
        }
        
        self.changes.append(change_entry)
        self.save_logs()
        
        # Affichage console avec couleurs emoji
        impact_emoji = {
            "low": "🟢",
            "normal": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }
        
        type_emoji = {
            "feature": "✨",
            "bugfix": "🐛",
            "improvement": "⚡",
            "security": "🛡️",
            "ui": "🎨",
            "performance": "🚀",
            "api": "🔌",
            "database": "💾"
        }
        
        print(f"{impact_emoji.get(impact, '⚪')} {type_emoji.get(change_type, '📝')} [{component.upper()}] {description}")
        
        return change_entry["id"]
        
    def _categorize_change(self, change_type: str, component: str) -> str:
        """Catégoriser automatiquement le changement"""
        if component in ["webpanel", "gui", "interface"]:
            return "Frontend"
        elif component in ["bot", "discord", "commands"]:
            return "Bot Discord"
        elif component in ["api", "server", "backend"]:
            return "Backend"
        elif component in ["database", "data", "storage"]:
            return "Database"
        elif component in ["security", "auth", "oauth"]:
            return "Security"
        else:
            return "General"
            
    def get_changes_for_version(self, version: str = "V4.2.1") -> List[Dict]:
        """Récupérer les changements pour une version"""
        return [c for c in self.changes if c.get("version") == version]
        
    def get_changes_by_type(self, change_type: str) -> List[Dict]:
        """Récupérer les changements par type"""
        return [c for c in self.changes if c.get("change_type") == change_type]
        
    def get_recent_changes(self, hours: int = 24) -> List[Dict]:
        """Récupérer les changements récents"""
        cutoff = time.time() - (hours * 3600)
        return [c for c in self.changes if c.get("timestamp", 0) > cutoff]
        
    def generate_changelog_markdown(self, version: str = "V4.2.1") -> str:
        """Générer un changelog en Markdown"""
        changes = self.get_changes_for_version(version)
        
        if not changes:
            return f"# Changelog {version}\n\nAucun changement enregistré pour cette version."
            
        # Organiser par catégorie
        categories = {}
        for change in changes:
            category = change.get("category", "General")
            if category not in categories:
                categories[category] = []
            categories[category].append(change)
            
        # Générer le markdown
        markdown = f"# 🚀 Arsenal V4 - Changelog {version}\n\n"
        markdown += f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        markdown += f"**Total des changements:** {len(changes)}\n\n"
        
        for category, cat_changes in categories.items():
            markdown += f"## 📂 {category}\n\n"
            
            # Organiser par type dans chaque catégorie
            types = {}
            for change in cat_changes:
                change_type = change.get("change_type", "other")
                if change_type not in types:
                    types[change_type] = []
                types[change_type].append(change)
                
            for change_type, type_changes in types.items():
                type_emoji = {
                    "feature": "✨ **Nouvelles Fonctionnalités**",
                    "improvement": "⚡ **Améliorations**", 
                    "bugfix": "🐛 **Corrections de Bugs**",
                    "security": "🛡️ **Sécurité**",
                    "ui": "🎨 **Interface Utilisateur**",
                    "performance": "🚀 **Performance**",
                    "api": "🔌 **API**",
                    "database": "💾 **Base de Données**"
                }
                
                markdown += f"### {type_emoji.get(change_type, '📝 **Autres**')}\n\n"
                
                for change in type_changes:
                    impact_indicator = {
                        "critical": "🔴",
                        "high": "🟠", 
                        "normal": "🟡",
                        "low": "🟢"
                    }.get(change.get("impact", "normal"), "⚪")
                    
                    markdown += f"- {impact_indicator} {change['description']}\n"
                    
                    if change.get("details"):
                        for detail_key, detail_value in change["details"].items():
                            markdown += f"  - **{detail_key}:** {detail_value}\n"
                    
                markdown += "\n"
                
        markdown += "---\n"
        markdown += "*Généré automatiquement par Arsenal Change Logger*\n"
        
        return markdown
        
    def export_changelog(self, version: str = "V4.2.1", format: str = "markdown"):
        """Exporter le changelog"""
        filename = f"CHANGELOG_{version}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if format == "markdown":
            content = self.generate_changelog_markdown(version)
            filename += ".md"
        else:
            changes = self.get_changes_for_version(version)
            content = json.dumps(changes, indent=2, ensure_ascii=False)
            filename += ".json"
            
        filepath = os.path.join("logs", filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Changelog exporté: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Erreur export changelog: {e}")
            return None
            
    def get_stats(self) -> Dict:
        """Statistiques des changements"""
        if not self.changes:
            return {"total": 0}
            
        stats = {
            "total": len(self.changes),
            "by_type": {},
            "by_category": {},
            "by_impact": {},
            "recent_24h": len(self.get_recent_changes(24)),
            "current_session": len([c for c in self.changes if c.get("session_id") == self.session_id])
        }
        
        for change in self.changes:
            # Par type
            change_type = change.get("change_type", "other")
            stats["by_type"][change_type] = stats["by_type"].get(change_type, 0) + 1
            
            # Par catégorie
            category = change.get("category", "General")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Par impact
            impact = change.get("impact", "normal")
            stats["by_impact"][impact] = stats["by_impact"].get(impact, 0) + 1
            
        return stats

# Instance globale
change_logger = ArsenalChangeLogger()

# Fonctions utilitaires rapides
def log_feature(component: str, description: str, details: Dict = None, impact: str = "normal"):
    """Logger une nouvelle fonctionnalité"""
    return change_logger.log_change("feature", component, description, details, impact)

def log_bugfix(component: str, description: str, details: Dict = None, impact: str = "normal"):
    """Logger une correction de bug"""
    return change_logger.log_change("bugfix", component, description, details, impact)

def log_improvement(component: str, description: str, details: Dict = None, impact: str = "normal"):
    """Logger une amélioration"""
    return change_logger.log_change("improvement", component, description, details, impact)

def log_ui_change(component: str, description: str, details: Dict = None, impact: str = "normal"):
    """Logger un changement d'interface"""
    return change_logger.log_change("ui", component, description, details, impact)

def log_api_change(component: str, description: str, details: Dict = None, impact: str = "normal"):
    """Logger un changement d'API"""
    return change_logger.log_change("api", component, description, details, impact)

if __name__ == "__main__":
    # Test du système
    print("🚀 Test du système de logging des changements")
    
    # Exemples de logs
    log_feature("gui", "Création de l'interface suprême Arsenal", {
        "file": "ArsenalSuperGui.py",
        "lines": "400+",
        "features": ["Dashboard moderne", "Menu sidebar", "Actions rapides"]
    }, "high")
    
    log_improvement("webpanel", "Ajout de nouvelles APIs", {
        "apis": ["monitoring", "analytics", "security"],
        "endpoints": 7
    }, "normal")
    
    log_bugfix("webpanel", "Correction sidebar navigation", {
        "issue": "Navigation entre pages cassée",
        "solution": "Réparation fonction showPage()"
    }, "normal")
    
    # Afficher les stats
    stats = change_logger.get_stats()
    print(f"\n📊 Statistiques des changements:")
    print(f"  Total: {stats['total']}")
    print(f"  Session actuelle: {stats['current_session']}")
    print(f"  Dernières 24h: {stats['recent_24h']}")
    
    # Générer le changelog
    changelog_file = change_logger.export_changelog()
    print(f"\n📄 Changelog généré: {changelog_file}")
