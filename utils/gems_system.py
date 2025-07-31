#!/usr/bin/env python3
"""
💎 HUNT ROYAL GEMS SYSTEM
========================

Système de gemmes Hunt Royal avec données réelles niveau 7
Basé sur les vraies statistiques du jeu
"""

import json
import os
from typing import Dict, List, Optional, Any

class HuntRoyalGemsSystem:
    """Système de gestion des gemmes Hunt Royal"""
    
    def __init__(self, json_path: str = None):
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), "..", "data", "gems_stats.json")
        
        self.json_path = json_path
        self.gems_data = self._load_gems_data()
    
    def _load_gems_data(self) -> Dict[str, Any]:
        """Charger les données des gemmes depuis le JSON"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Fichier {self.json_path} non trouvé")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON : {e}")
            return {}
    
    def get_all_gems_level_7(self) -> Dict[str, Any]:
        """Récupérer toutes les gemmes niveau 7"""
        return self.gems_data.get("gems_level_7", {})
    
    def get_gem_by_id(self, gem_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer une gemme par son ID"""
        gems = self.get_all_gems_level_7()
        for gem_key, gem_data in gems.items():
            if gem_data.get("id") == gem_id:
                return gem_data
        return None
    
    def get_gem_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupérer une gemme par son nom (recherche flexible)"""
        gems = self.get_all_gems_level_7()
        name_lower = name.lower()
        
        for gem_key, gem_data in gems.items():
            gem_name = gem_data.get("name", "").lower()
            if name_lower in gem_name or gem_name in name_lower:
                return gem_data
        return None
    
    def get_gems_by_color(self, color: str) -> List[Dict[str, Any]]:
        """Récupérer les gemmes par couleur"""
        gems = self.get_all_gems_level_7()
        color_lower = color.lower()
        result = []
        
        for gem_key, gem_data in gems.items():
            if color_lower in gem_key.lower():
                result.append(gem_data)
        
        return result
    
    def get_gems_for_equipment_type(self, equipment_type: str) -> List[Dict[str, Any]]:
        """Récupérer les gemmes compatibles avec un type d'équipement"""
        gems = self.get_all_gems_level_7()
        result = []
        
        for gem_key, gem_data in gems.items():
            compatible = gem_data.get("compatible_equipment", {})
            if equipment_type in compatible.get("armor", []) or equipment_type in compatible.get("weapon", []):
                result.append(gem_data)
        
        return result
    
    def calculate_build_power(self, gem_ids: List[str]) -> Dict[str, Any]:
        """Calculer la puissance totale d'un build"""
        total_power = 0
        gems_used = []
        effects_summary = {"armor": [], "weapon": []}
        
        for gem_id in gem_ids:
            gem = self.get_gem_by_id(gem_id)
            if gem:
                total_power += gem.get("power", 0)
                gems_used.append(gem)
                
                # Ajouter les effets
                effects = gem.get("effects", {})
                if "armor" in effects:
                    effects_summary["armor"].append(effects["armor"])
                if "weapon" in effects:
                    effects_summary["weapon"].append(effects["weapon"])
        
        return {
            "total_power": total_power,
            "gems_count": len(gems_used),
            "gems_used": gems_used,
            "effects_summary": effects_summary,
            "is_max_normal": total_power >= 9000,  # 15 gems x 600
            "is_max_titan": total_power >= 12000   # 20 gems x 600
        }
    
    def get_optimal_builds(self, focus: str = "damage") -> List[Dict[str, Any]]:
        """Suggérer des builds optimaux selon le focus"""
        gems = self.get_all_gems_level_7()
        builds = []
        
        if focus == "damage":
            # Build DPS : Rouge, Blanche, Jaune
            damage_gems = ["red_power_stone", "white_power_stone", "yellow_power_stone"]
            builds.append({
                "name": "Build DPS Maximum",
                "focus": "Dégâts",
                "gems": damage_gems,
                "description": "Maximise les dégâts avec brûlure, dégâts purs et vitesse d'attaque"
            })
        
        elif focus == "tank":
            # Build Tank : Bleue, Verte, Azure
            tank_gems = ["blue_power_stone", "green_power_stone", "azure_power_stone"]
            builds.append({
                "name": "Build Tank Ultime",
                "focus": "Survie", 
                "gems": tank_gems,
                "description": "Maximise la défense avec réduction dégâts, HP et contrôle"
            })
        
        elif focus == "utility":
            # Build Utilitaire : Violette, Jaune, Verte
            utility_gems = ["purple_power_stone", "yellow_power_stone", "green_power_stone"]
            builds.append({
                "name": "Build Farming XP",
                "focus": "Utilitaire",
                "gems": utility_gems,
                "description": "Optimisé pour le farm avec bonus XP, vitesse et HP"
            })
        
        return builds
    
    def get_equipment_info(self) -> Dict[str, Any]:
        """Récupérer les infos sur les équipements"""
        return self.gems_data.get("equipment_types", {})
    
    def get_system_info(self) -> Dict[str, Any]:
        """Récupérer les infos système"""
        return self.gems_data.get("gems_system", {})
    
    def format_gem_info(self, gem: Dict[str, Any]) -> str:
        """Formater les infos d'une gemme pour affichage"""
        if not gem:
            return "Gemme non trouvée"
        
        name = gem.get("name", "Gemme inconnue")
        power = gem.get("power", 0)
        level = gem.get("level", 0)
        
        effects = gem.get("effects", {})
        armor_effect = effects.get("armor", {})
        weapon_effect = effects.get("weapon", {})
        
        result = f"💎 **{name}** (Niveau {level})\n"
        result += f"⚡ Puissance: {power}\n\n"
        
        if armor_effect:
            result += f"🛡️ **Effet Armure:** {armor_effect.get('description', 'N/A')}\n"
        
        if weapon_effect:
            result += f"⚔️ **Effet Arme:** {weapon_effect.get('description', 'N/A')}\n"
        
        return result

# Fonction utilitaire pour tests rapides
def test_gems_system():
    """Tester le système de gemmes"""
    print("🧪 Test du système de gemmes Hunt Royal")
    print("=" * 50)
    
    gems_system = HuntRoyalGemsSystem()
    
    # Test 1: Toutes les gemmes
    all_gems = gems_system.get_all_gems_level_7()
    print(f"✅ {len(all_gems)} gemmes niveau 7 chargées")
    
    # Test 2: Gemme spécifique
    red_gem = gems_system.get_gem_by_id("red_power_stone")
    if red_gem:
        print(f"✅ Gemme rouge trouvée: {red_gem['name']}")
        print(f"   Power: {red_gem['power']}")
        print(f"   Effet armure: {red_gem['effects']['armor']['description']}")
        print(f"   Effet arme: {red_gem['effects']['weapon']['description']}")
    
    # Test 3: Build calculator
    test_build = ["red_power_stone", "blue_power_stone", "yellow_power_stone"]
    build_result = gems_system.calculate_build_power(test_build)
    print(f"✅ Build test: {build_result['total_power']} power avec {build_result['gems_count']} gemmes")
    
    print("=" * 50)
    print("✅ Test terminé !")

if __name__ == "__main__":
    test_gems_system()
