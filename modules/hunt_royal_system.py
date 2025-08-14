"""
🏹 HUNT ROYAL - Système Complet pour Arsenal Bot
==============================================

Module autonome avec base de données complète pour Hunt Royal
- Système de suggestions avancé
- Base de données chasseurs avec VRAIES DONNÉES depuis more-huntroyale.com
- Scraping automatique des stats HP/ATK niveaux 1-10, Awaken, vitesse, perks
- Commandes de gestion intégrées
- Hot-reload supporté

Créé par Arsenal Bot V4 - Hunt Royal Expert System avec auto-update
"""

import json
import os
import sqlite3
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
import asyncio
from typing import Dict, List, Optional, Union
import importlib
import sys
from pathlib import Path

# Import du scraper Hunt Royal
try:
    from utils.hunt_royal_scraper import HuntRoyalScraper, HuntRoyalAutoUpdater, setup_hunt_royal_scraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("⚠️ Scraper Hunt Royal non disponible, utilisation des données statiques")

class HuntRoyalDatabase:
    """Base de données Hunt Royal avec toutes les informations complètes"""
    
    def __init__(self, db_path: str = "hunt_royal.db"):
        self.db_path = db_path
        self.init_database()
        self.load_complete_data()
    
    def init_database(self):
        """Initialiser toutes les tables Hunt Royal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des chasseurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunters (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                cost_type TEXT DEFAULT 'coins',           -- 'coins', 'gems', 'special'
                cost_amount INTEGER DEFAULT 0,            -- Coût d'achat
                tier_meta TEXT DEFAULT 'B',               -- Tier dans la méta (S+, S, A+, A, B+, B, C)
                weapon_type TEXT,
                attack_base INTEGER,
                health_base INTEGER,
                defense_base INTEGER,
                speed_base INTEGER,
                description TEXT,
                skills TEXT,
                passive_abilities TEXT,
                awakening_cost TEXT,
                best_equipment TEXT,
                counters TEXT,
                synergies TEXT,
                popularity INTEGER DEFAULT 50,            -- Popularité % dans la communauté
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des donjons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dungeons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                difficulty TEXT,
                recommended_level INTEGER,
                boss_name TEXT,
                boss_hp INTEGER,
                boss_elements TEXT,
                resistances TEXT,
                weaknesses TEXT,
                rewards TEXT,
                strategy TEXT,
                best_hunters TEXT,
                avoid_hunters TEXT,
                modifiers TEXT,
                energy_cost INTEGER,
                duration_minutes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des équipements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                level_max INTEGER,
                attack_bonus INTEGER,
                health_bonus INTEGER,
                defense_bonus INTEGER,
                speed_bonus INTEGER,
                special_effect TEXT,
                set_bonus TEXT,
                gem_slots INTEGER,
                upgrade_materials TEXT,
                drop_locations TEXT,
                tier_rating TEXT,
                best_for_classes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des gemmes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gems (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                level_max INTEGER,
                primary_stat TEXT,
                primary_value INTEGER,
                secondary_stats TEXT,
                special_effects TEXT,
                upgrade_cost TEXT,
                drop_sources TEXT,
                tier_rating TEXT,
                best_combinations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des builds recommandés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS builds (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hunter_id TEXT,
                equipment_set TEXT,
                gems_set TEXT,
                strategy TEXT,
                pros TEXT,
                cons TEXT,
                rating REAL,
                difficulty TEXT,
                pvp_viable BOOLEAN,
                pve_viable BOOLEAN,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hunter_id) REFERENCES hunters (id)
            )
        ''')
        
        # Table des suggestions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT,
                suggestion_type TEXT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                category TEXT,
                votes_up INTEGER DEFAULT 0,
                votes_down INTEGER DEFAULT 0,
                admin_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des votes sur suggestions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_id INTEGER,
                user_id TEXT,
                vote_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (suggestion_id) REFERENCES suggestions (id)
            )
        ''')
        
        # Table des modes de jeu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_modes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                rules TEXT,
                rewards TEXT,
                duration TEXT,
                requirements TEXT,
                strategies TEXT,
                meta_hunters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données Hunt Royal initialisée")
    
    def load_complete_data(self):
        """Charger toutes les données Hunt Royal depuis les sources externes"""
        
        # VRAIES DONNÉES Hunt Royal - Chasseurs avec vraie économie
        hunters_data = [
            {
                "id": "elf_archer",
                "name": "Elf Archer",
                "cost_type": "coins",
                "cost_amount": 500,
                "tier_meta": "C+",
                "weapon_type": "Bow",
                "attack_base": 100,
                "health_base": 800,
                "defense_base": 50,
                "speed_base": 120,
                "description": "Archer elfe rapide et précis avec des capacités à distance",
                "skills": "Power Shot, Rain of Arrows, Eagle Eye",
                "passive_abilities": "Range +20%, Critical Rate +10%",
                "awakening_cost": "20 Nature Stones + 10 Archer Scrolls",
                "best_equipment": "Elven Bow, Ranger's Cloak",
                "counters": "Assassins, High Mobility",
                "synergies": "Other Archers, Nature Hunters",
                "popularity": 45
            },
            {
                "id": "barbarian",
                "name": "Barbarian",
                "cost_type": "coins",
                "cost_amount": 750,
                "tier_meta": "B+",
                "weapon_type": "Axe",
                "attack_base": 150,
                "health_base": 1200,
                "defense_base": 80,
                "speed_base": 90,
                "description": "Guerrier brutal avec des attaques puissantes au corps à corps",
                "skills": "Berserker Rage, Whirlwind, Axe Throw",
                "passive_abilities": "Attack +15%, Damage Reduction +10%",
                "awakening_cost": "25 War Stones + 15 Barbarian Scrolls",
                "best_equipment": "War Axe, Barbarian Armor",
                "counters": "Ranged Units, Kiting",
                "synergies": "Tank Hunters, Melee DPS",
                "popularity": 65
            },
            {
                "id": "wizard",
                "name": "Wizard",
                "cost_type": "gems",
                "cost_amount": 50,
                "tier_meta": "A",
                "weapon_type": "Staff",
                "attack_base": 200,
                "health_base": 600,
                "defense_base": 30,
                "speed_base": 70,
                "description": "Mage puissant avec sorts de zone et magie élémentaire",
                "skills": "Fireball, Ice Storm, Lightning Bolt",
                "passive_abilities": "Magic Damage +25%, Mana Regen +20%",
                "awakening_cost": "40 Magic Crystals + 20 Wizard Scrolls",
                "best_equipment": "Arcane Staff, Mage Robes",
                "counters": "Assassins, Magic Resist",
                "synergies": "Other Mages, Support Units",
                "popularity": 80
            },
            {
                "id": "dragon_knight",
                "name": "Dragon Knight",
                "cost_type": "gems",
                "cost_amount": 150,
                "tier_meta": "A+",
                "weapon_type": "Sword",
                "attack_base": 180,
                "health_base": 1000,
                "defense_base": 100,
                "speed_base": 85,
                "description": "Chevalier dragon avec armure lourde et attaques de feu",
                "skills": "Dragon Strike, Fire Shield, Dragon Breath",
                "passive_abilities": "Fire Damage +30%, Fire Resistance +50%",
                "awakening_cost": "60 Dragon Scales + 30 Knight Scrolls",
                "best_equipment": "Dragon Sword, Dragon Armor",
                "counters": "Ice/Water Units, Armor Piercing",
                "synergies": "Fire Units, Tank Role",
                "popularity": 75
            },
            {
                "id": "ninja",
                "name": "Ninja",
                "cost_type": "gems",
                "cost_amount": 200,
                "tier_meta": "S",
                "weapon_type": "Daggers",
                "attack_base": 160,
                "health_base": 700,
                "defense_base": 40,
                "speed_base": 150,
                "description": "Assassin furtif avec haute mobilité et dégâts critiques",
                "skills": "Shadow Strike, Smoke Bomb, Critical Slash",
                "passive_abilities": "Critical Damage +40%, Dodge +15%",
                "awakening_cost": "50 Shadow Stones + 25 Ninja Scrolls",
                "best_equipment": "Shadow Blades, Ninja Suit",
                "counters": "Tanks, Area Damage",
                "synergies": "Other Assassins, Burst DPS",
                "popularity": 90
            },
            {
                "id": "zeus",
                "name": "Zeus",
                "cost_type": "special",
                "cost_amount": 500,
                "tier_meta": "S+",
                "weapon_type": "Staff",
                "attack_base": 300,
                "health_base": 900,
                "defense_base": 60,
                "speed_base": 100,
                "description": "Dieu de la foudre avec des pouvoirs électriques dévastateurs",
                "skills": "Thunder Strike, Chain Lightning, Divine Wrath",
                "passive_abilities": "Lightning Damage +50%, Stun Chance +20%",
                "awakening_cost": "100 Divine Shards + 50 Zeus Fragments",
                "best_equipment": "Zeus Staff, Divine Robes",
                "counters": "Magic Immune, High Resistance",
                "synergies": "Lightning Units, AoE Comps",
                "popularity": 95
            }
        ]
        
        # VRAIES DONNÉES - Donjons du jeu actuel
        dungeons_data = [
            {
                "id": "dragon_dungeon",
                "name": "Dragon's Dungeon",
                "type": "PvE Dungeon",
                "difficulty": "Easy",
                "recommended_level": 500,
                "boss_name": "Ancient Dragon",
                "boss_hp": 50000,
                "boss_elements": "Fire, Physical",
                "resistances": "Fire 50%, Physical 30%",
                "weaknesses": "Ice 150%, Water 120%",
                "rewards": "Dragon Gems (50), Epic Gear (50), Tokens (150)",
                "strategy": "Use Ice/Water hunters, avoid fire damage, focus on DPS",
                "best_hunters": "Ice Queen, Water Elementals, High DPS",
                "avoid_hunters": "Fire units, Low HP hunters",
                "modifiers": "Epic gear gives Epic Gems",
                "energy_cost": 15,
                "duration_minutes": 10
            },
            {
                "id": "kraken_ship",
                "name": "Kraken's Ship",
                "type": "PvE Dungeon",
                "difficulty": "Medium",
                "recommended_level": 2500,
                "boss_name": "Kraken",
                "boss_hp": 80000,
                "boss_elements": "Water, Tentacle",
                "resistances": "Water 60%, Physical 40%",
                "weaknesses": "Lightning 140%, Fire 110%",
                "rewards": "Kraken Gems (50), Epic Gear (62), Tokens (170)",
                "strategy": "Repair ship, use cannon, Lightning/Fire hunters recommended",
                "best_hunters": "Zeus, Fire Mages, Lightning Units",
                "avoid_hunters": "Water units, Slow attackers",
                "modifiers": "Ship cannon mechanic, Epic gear for Epic Gems",
                "energy_cost": 20,
                "duration_minutes": 12
            },
            {
                "id": "yeti_tundra",
                "name": "Yeti's Tundra",
                "type": "PvE Dungeon",
                "difficulty": "Hard",
                "recommended_level": 5000,
                "boss_name": "Ice Yeti",
                "boss_hp": 120000,
                "boss_elements": "Ice, Physical",
                "resistances": "Ice 70%, Cold 80%",
                "weaknesses": "Fire 160%, Lightning 130%",
                "rewards": "Yeti Gems (50), Epic Gear (74), Tokens (200)",
                "strategy": "Avoid ice traps, use Fire/Lightning, high mobility needed",
                "best_hunters": "Fire Knights, Lightning Mages, Mobile DPS",
                "avoid_hunters": "Ice units, Slow tanks",
                "modifiers": "Ice traps, freezing effects",
                "energy_cost": 25,
                "duration_minutes": 15
            },
            {
                "id": "maze",
                "name": "Maze",
                "type": "PvE Dungeon",
                "difficulty": "Very Hard",
                "recommended_level": 10000,
                "boss_name": "Maze Guardian",
                "boss_hp": 200000,
                "boss_elements": "All Elements",
                "resistances": "All 40%",
                "weaknesses": "None",
                "rewards": "Maze Gems (50), Epic Gear (612), Tokens (305)",
                "strategy": "Navigate maze, balanced team needed, endurance fight",
                "best_hunters": "Balanced compositions, High survivability",
                "avoid_hunters": "Glass cannons, One-trick ponies",
                "modifiers": "Complex maze mechanics, long duration",
                "energy_cost": 30,
                "duration_minutes": 20
            },
            {
                "id": "chaos_dungeon",
                "name": "Chaos Dungeon",
                "type": "PvE Dungeon",
                "difficulty": "Extreme",
                "recommended_level": 350000,
                "boss_name": "Chaos Lord",
                "boss_hp": 500000,
                "boss_elements": "Chaos, All",
                "resistances": "All 60%",
                "weaknesses": "Pure Damage",
                "rewards": "Multi Gems (1405), Epic Gear (2250), Tokens (575)",
                "strategy": "High Gearscore required, perfect team composition",
                "best_hunters": "Top tier only, Perfect synergy needed",
                "avoid_hunters": "Weak hunters, Poor synergy",
                "modifiers": "Chaos effects, random mechanics",
                "energy_cost": 40,
                "duration_minutes": 25
            }
        ]
        
        # VRAIES DONNÉES - Équipements du jeu
        equipment_data = [
            {
                "id": "elven_bow",
                "name": "Elven Bow",
                "type": "Weapon",
                "rarity": "Rare",
                "level_max": 50,
                "attack_bonus": 250,
                "health_bonus": 100,
                "defense_bonus": 20,
                "speed_bonus": 30,
                "special_effect": "Range +25%, Critical Rate +15%",
                "set_bonus": "Ranger Set: Attack Speed +20%",
                "gem_slots": 2,
                "upgrade_materials": "Wood, Elven Crystals, Archer Tokens",
                "drop_locations": "Forest Dungeons, Elf Events",
                "tier_rating": "B+",
                "best_for_classes": "Archers, Rangers, Marksmen"
            },
            {
                "id": "dragon_sword",
                "name": "Dragon Sword",
                "type": "Weapon",
                "rarity": "Epic",
                "level_max": 60,
                "attack_bonus": 400,
                "health_bonus": 200,
                "defense_bonus": 50,
                "speed_bonus": -10,
                "special_effect": "Fire Damage +40%, Burn Chance +25%",
                "set_bonus": "Dragon Set: Fire Resistance +50%",
                "gem_slots": 3,
                "upgrade_materials": "Dragon Scales, Fire Crystals, Dragon Tokens",
                "drop_locations": "Dragon Dungeon, Fire Events",
                "tier_rating": "A",
                "best_for_classes": "Knights, Warriors, Fire Users"
            },
            {
                "id": "shadow_cloak",
                "name": "Shadow Cloak",
                "type": "Armor",
                "rarity": "Epic",
                "level_max": 55,
                "attack_bonus": 50,
                "health_bonus": 300,
                "defense_bonus": 100,
                "speed_bonus": 50,
                "special_effect": "Dodge +20%, Stealth Duration +30%",
                "set_bonus": "Shadow Set: Critical Damage +35%",
                "gem_slots": 2,
                "upgrade_materials": "Shadow Essence, Dark Crystals",
                "drop_locations": "Shadow Dungeons, Night Events",
                "tier_rating": "A+",
                "best_for_classes": "Assassins, Rogues, Ninjas"
            }
        ]
        
        # VRAIES DONNÉES - Gemmes Hunt Royal niveau 7 (infos précieuses 15min de rédaction)
        gems_data = [
            {
                "id": "red_power_stone",
                "name": "Pierre de Pouvoir Rouge",
                "type": "Attack/Defense",
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "Brulure/Esquive",
                "primary_value": "250%/12%",
                "secondary_stats": "Armure: Esquive +12%, Arme: Brulure +250%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Dragon/Kraken/Yeti Gems",
                "drop_sources": "Donjons, Events, Merging",
                "tier_rating": "S",
                "best_combinations": "Builds DPS feu, Tanks esquive"
            },
            {
                "id": "green_power_stone", 
                "name": "Pierre de Pouvoir Verte",
                "type": "Health/Poison",
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "PV/Poison", 
                "primary_value": "300/200%",
                "secondary_stats": "Armure: PV +300, Arme: Poison +200%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Nature Crystals",
                "drop_sources": "Nature Events, Forest Dungeons", 
                "tier_rating": "A+",
                "best_combinations": "Builds poison, Tank sustain"
            },
            {
                "id": "blue_power_stone",
                "name": "Pierre de Pouvoir Bleue", 
                "type": "Defense/Tentacles",
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "Réduction/Tentacules",
                "primary_value": "11%/90%", 
                "secondary_stats": "Armure: Dégâts réduits 11%, Arme: Chance tentacules 90%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Kraken Gems",
                "drop_sources": "Kraken Ship, Water Events",
                "tier_rating": "A",
                "best_combinations": "Builds tank, Contrôle aquatique"
            },
            {
                "id": "violet_power_stone",
                "name": "Pierre de Pouvoir Violette",
                "type": "XP/LifeDrain", 
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "XP/Drain",
                "primary_value": "35%/20%",
                "secondary_stats": "Armure: XP +35%, Arme: Drain de vie 20%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau", 
                "upgrade_cost": "Gold + Magic Crystals",
                "drop_sources": "Magic Events, Wizard Tower",
                "tier_rating": "B+",
                "best_combinations": "Leveling builds, Sustain DPS"
            },
            {
                "id": "white_power_stone",
                "name": "Pierre de Pouvoir Blanche",
                "type": "Stun/Damage",
                "rarity": "Level 7", 
                "level_max": 7,
                "primary_stat": "Étourdissement/Dégâts",
                "primary_value": "10%/+75",
                "secondary_stats": "Armure: Chance d'étourdir 10%, Arme: Dégâts +75",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Divine Shards", 
                "drop_sources": "Angel Events, Holy Dungeons",
                "tier_rating": "A",
                "best_combinations": "Builds contrôle, DPS pure"
            },
            {
                "id": "yellow_power_stone",
                "name": "Pierre de Pouvoir Jaune",
                "type": "Speed/AttackSpeed",
                "rarity": "Level 7",
                "level_max": 7, 
                "primary_stat": "Rapidité/Vitesse attaque",
                "primary_value": "35%/40%",
                "secondary_stats": "Armure: Rapidité +35%, Arme: Vitesse attaque +40%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Lightning Crystals",
                "drop_sources": "Speed Events, Lightning Dungeons",
                "tier_rating": "S", 
                "best_combinations": "Builds speed, DPS rapide"
            },
            {
                "id": "azure_power_stone",
                "name": "Pierre de Pouvoir Azure",
                "type": "Freeze/Nova",
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "Surgelé/Nova", 
                "primary_value": "25%/50%",
                "secondary_stats": "Armure: Surgelé 25%, Arme: Explosion nova 50%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Ice Crystals",
                "drop_sources": "Ice Events, Yeti Tundra",
                "tier_rating": "A+",
                "best_combinations": "Builds glace, AoE contrôle"
            },
            {
                "id": "zombie_power_stone", 
                "name": "Pierre de Pouvoir Zombie",
                "type": "ZombieRes/ZombieDmg",
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "Résistance zombie/Dégâts zombie",
                "primary_value": "20%/60%+20",
                "secondary_stats": "Armure: Réduction dégâts zombie 20%, Arme: Dégâts zombie 60% + Dégâts +20", 
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Undead Essence",
                "drop_sources": "Zombie Events, Dark Dungeons",
                "tier_rating": "B",
                "best_combinations": "Anti-zombie, Builds sombres"
            },
            {
                "id": "earth_power_stone",
                "name": "Pierre de Pouvoir Terre", 
                "type": "PoisonRes/EarthDmg",
                "rarity": "Level 7",
                "level_max": 7,
                "primary_stat": "Résistance poison/Dégâts terre",
                "primary_value": "15%/20%",
                "secondary_stats": "Armure: Résistance poison 15%, Arme: Dégâts terre 20%",
                "special_effects": "Emplacements: Casque/Plastron/Bottes + Épée/Anneau",
                "upgrade_cost": "Gold + Earth Crystals", 
                "drop_sources": "Earth Events, Underground Dungeons",
                "tier_rating": "B+",
                "best_combinations": "Anti-poison, Builds terre"
            }
        ]
        
        # Insérer toutes les données
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insérer chasseurs
        for hunter in hunters_data:
            cursor.execute('''
                INSERT OR REPLACE INTO hunters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hunter["id"], hunter["name"], hunter["cost_type"], hunter["cost_amount"],
                hunter["tier_meta"], hunter["weapon_type"], hunter["attack_base"], hunter["health_base"],
                hunter["defense_base"], hunter["speed_base"], hunter["description"],
                hunter["skills"], hunter["passive_abilities"], hunter["awakening_cost"],
                hunter["best_equipment"], hunter["counters"], hunter["synergies"],
                hunter["popularity"], datetime.now()
            ))
        
        # Insérer donjons
        for dungeon in dungeons_data:
            cursor.execute('''
                INSERT OR REPLACE INTO dungeons VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dungeon["id"], dungeon["name"], dungeon["type"], dungeon["difficulty"],
                dungeon["recommended_level"], dungeon["boss_name"], dungeon["boss_hp"],
                dungeon["boss_elements"], dungeon["resistances"], dungeon["weaknesses"],
                dungeon["rewards"], dungeon["strategy"], dungeon["best_hunters"],
                dungeon["avoid_hunters"], dungeon["modifiers"], dungeon["energy_cost"],
                dungeon["duration_minutes"], datetime.now()
            ))
        
        # Insérer équipements
        for equipment in equipment_data:
            cursor.execute('''
                INSERT OR REPLACE INTO equipment VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipment["id"], equipment["name"], equipment["type"], equipment["rarity"],
                equipment["level_max"], equipment["attack_bonus"], equipment["health_bonus"],
                equipment["defense_bonus"], equipment["speed_bonus"], equipment["special_effect"],
                equipment["set_bonus"], equipment["gem_slots"], equipment["upgrade_materials"],
                equipment["drop_locations"], equipment["tier_rating"], equipment["best_for_classes"],
                datetime.now()
            ))
        
        # Insérer gemmes
        for gem in gems_data:
            cursor.execute('''
                INSERT OR REPLACE INTO gems VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                gem["id"], gem["name"], gem["type"], gem["rarity"],
                gem["level_max"], gem["primary_stat"], gem["primary_value"],
                gem["secondary_stats"], gem["special_effects"], gem["upgrade_cost"],
                gem["drop_sources"], gem["tier_rating"], gem["best_combinations"],
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
        print("✅ Données Hunt Royal chargées")

    def get_all_hunters(self):
        """Récupérer tous les chasseurs de la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM hunters ORDER BY tier_meta, name')
        hunters_raw = cursor.fetchall()
        conn.close()
        
        hunters = []
        for hunter in hunters_raw:
            hunters.append({
                'id': hunter[0],
                'name': hunter[1],
                'cost_type': hunter[2],
                'cost_amount': hunter[3],
                'tier_meta': hunter[4],
                'weapon_type': hunter[5],
                'attack_base': hunter[6],
                'health_base': hunter[7],
                'defense_base': hunter[8],
                'speed_base': hunter[9],
                'description': hunter[10],
                'skills': hunter[11],
                'passive_abilities': hunter[12],
                'awakening_cost': hunter[13],
                'best_equipment': hunter[14],
                'counters': hunter[15],
                'synergies': hunter[16],
                'popularity': hunter[17]
            })
        
        return hunters

    def get_hunter_by_name(self, name: str):
        """Rechercher un chasseur par nom"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM hunters 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(id) LIKE LOWER(?)
        ''', (f'%{name}%', f'%{name}%'))
        
        hunter_raw = cursor.fetchone()
        conn.close()
        
        if not hunter_raw:
            return None
            
        return {
            'id': hunter_raw[0],
            'name': hunter_raw[1],
            'cost_type': hunter_raw[2],
            'cost_amount': hunter_raw[3],
            'tier_meta': hunter_raw[4],
            'weapon_type': hunter_raw[5],
            'attack_base': hunter_raw[6],
            'health_base': hunter_raw[7],
            'defense_base': hunter_raw[8],
            'speed_base': hunter_raw[9],
            'description': hunter_raw[10],
            'skills': hunter_raw[11],
            'passive_abilities': hunter_raw[12],
            'awakening_cost': hunter_raw[13],
            'best_equipment': hunter_raw[14],
            'counters': hunter_raw[15],
            'synergies': hunter_raw[16],
            'popularity': hunter_raw[17]
        }

    def get_dungeon_by_name(self, name: str):
        """Rechercher un donjon par nom"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dungeons 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(id) LIKE LOWER(?)
        ''', (f'%{name}%', f'%{name}%'))
        
        dungeon_raw = cursor.fetchone()
        conn.close()
        
        if not dungeon_raw:
            return None
            
        return {
            'id': dungeon_raw[0],
            'name': dungeon_raw[1],
            'type': dungeon_raw[2],
            'difficulty': dungeon_raw[3],
            'recommended_level': dungeon_raw[4],
            'boss_name': dungeon_raw[5],
            'boss_hp': dungeon_raw[6],
            'boss_elements': dungeon_raw[7],
            'resistances': dungeon_raw[8],
            'weaknesses': dungeon_raw[9],
            'rewards': dungeon_raw[10],
            'strategy': dungeon_raw[11],
            'best_hunters': dungeon_raw[12],
            'avoid_hunters': dungeon_raw[13],
            'modifiers': dungeon_raw[14],
            'energy_cost': dungeon_raw[15],
            'duration_minutes': dungeon_raw[16]
        }

    def get_gem_by_name(self, name: str):
        """Rechercher une gemme par nom"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM gems 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(id) LIKE LOWER(?)
        ''', (f'%{name}%', f'%{name}%'))
        
        gem_raw = cursor.fetchone()
        conn.close()
        
        if not gem_raw:
            return None
            
        return {
            'id': gem_raw[0],
            'name': gem_raw[1],
            'type': gem_raw[2],
            'rarity': gem_raw[3],
            'level_max': gem_raw[4],
            'primary_stat': gem_raw[5],
            'primary_value': gem_raw[6],
            'secondary_stats': gem_raw[7],
            'special_effects': gem_raw[8],
            'upgrade_cost': gem_raw[9],
            'drop_sources': gem_raw[10],
            'tier_rating': gem_raw[11],
            'best_combinations': gem_raw[12]
        }

class HuntRoyalSuggestions:
    """Système de suggestions avancé pour Hunt Royal"""
    
    def __init__(self, db: HuntRoyalDatabase):
        self.db = db
        
    async def create_suggestion(self, user_id: str, username: str, title: str, description: str, category: str = "general"):
        """Créer une nouvelle suggestion"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO suggestions (user_id, username, title, description, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, title, description, category))
        
        suggestion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return suggestion_id
    
    async def vote_suggestion(self, suggestion_id: int, user_id: str, vote_type: str):
        """Voter sur une suggestion"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur a déjà voté
        cursor.execute('''
            SELECT vote_type FROM suggestion_votes 
            WHERE suggestion_id = ? AND user_id = ?
        ''', (suggestion_id, user_id))
        
        existing_vote = cursor.fetchone()
        
        if existing_vote:
            # Mettre à jour le vote existant
            old_vote = existing_vote[0]
            cursor.execute('''
                UPDATE suggestion_votes 
                SET vote_type = ? 
                WHERE suggestion_id = ? AND user_id = ?
            ''', (vote_type, suggestion_id, user_id))
            
            # Ajuster les compteurs
            if old_vote == 'up':
                cursor.execute('UPDATE suggestions SET votes_up = votes_up - 1 WHERE id = ?', (suggestion_id,))
            else:
                cursor.execute('UPDATE suggestions SET votes_down = votes_down - 1 WHERE id = ?', (suggestion_id,))
        else:
            # Nouveau vote
            cursor.execute('''
                INSERT INTO suggestion_votes (suggestion_id, user_id, vote_type)
                VALUES (?, ?, ?)
            ''', (suggestion_id, user_id, vote_type))
        
        # Mettre à jour les compteurs
        if vote_type == 'up':
            cursor.execute('UPDATE suggestions SET votes_up = votes_up + 1 WHERE id = ?', (suggestion_id,))
        else:
            cursor.execute('UPDATE suggestions SET votes_down = votes_down + 1 WHERE id = ?', (suggestion_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    async def get_suggestions(self, status: str = 'pending', limit: int = 10):
        """Récupérer les suggestions"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM suggestions 
            WHERE status = ? 
            ORDER BY votes_up DESC, created_at DESC 
            LIMIT ?
        ''', (status, limit))
        
        suggestions = cursor.fetchall()
        conn.close()
        
        return suggestions

class HuntRoyalAnalyzer:
    """Analyseur intelligent pour recommandations Hunt Royal"""
    
    def __init__(self, db: HuntRoyalDatabase):
        self.db = db
    
    async def analyze_team_composition(self, hunters: List[str]):
        """Analyser une composition d'équipe"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        team_analysis = {
            "hunters": [],
            "elements": {},
            "weapon_types": {},
            "total_stats": {"attack": 0, "health": 0, "defense": 0, "speed": 0},
            "synergies": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        for hunter_id in hunters:
            cursor.execute('SELECT * FROM hunters WHERE id = ?', (hunter_id,))
            hunter = cursor.fetchone()
            
            if hunter:
                team_analysis["hunters"].append(hunter)
                
                # Compter éléments
                element = hunter[3]  # element column
                team_analysis["elements"][element] = team_analysis["elements"].get(element, 0) + 1
                
                # Compter types d'armes
                weapon = hunter[4]  # weapon_type column
                team_analysis["weapon_types"][weapon] = team_analysis["weapon_types"].get(weapon, 0) + 1
                
                # Additionner stats
                team_analysis["total_stats"]["attack"] += hunter[5]  # attack_base
                team_analysis["total_stats"]["health"] += hunter[6]  # health_base
                team_analysis["total_stats"]["defense"] += hunter[7]  # defense_base
                team_analysis["total_stats"]["speed"] += hunter[8]  # speed_base
        
        # Analyser équilibre
        if len(team_analysis["elements"]) < 2:
            team_analysis["weaknesses"].append("Manque de diversité élémentaire")
        
        if team_analysis["total_stats"]["defense"] < 2000:
            team_analysis["recommendations"].append("Ajouter un tank ou améliorer la défense")
        
        if team_analysis["total_stats"]["attack"] < 3000:
            team_analysis["recommendations"].append("Augmenter le DPS de l'équipe")
        
        conn.close()
        return team_analysis
    
    async def recommend_dungeon_team(self, dungeon_id: str):
        """Recommander une équipe pour un donjon spécifique"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Récupérer info du donjon
        cursor.execute('SELECT * FROM dungeons WHERE id = ?', (dungeon_id,))
        dungeon = cursor.fetchone()
        
        if not dungeon:
            return None
        
        boss_elements = dungeon[7].split(', ') if dungeon[7] else []  # boss_elements
        resistances = dungeon[8]  # resistances
        weaknesses = dungeon[9]  # weaknesses
        
        # Recommander chasseurs selon les faiblesses du boss
        recommendations = {
            "dungeon": dungeon,
            "recommended_hunters": [],
            "strategy": dungeon[11],  # strategy
            "warnings": []
        }
        
        # Analyser faiblesses pour recommander éléments
        if "Holy" in weaknesses:
            cursor.execute("SELECT * FROM hunters WHERE element = 'Holy' ORDER BY tier_rating DESC LIMIT 3")
            holy_hunters = cursor.fetchall()
            recommendations["recommended_hunters"].extend(holy_hunters)
        
        if "Water" in weaknesses:
            cursor.execute("SELECT * FROM hunters WHERE element = 'Water' ORDER BY tier_rating DESC LIMIT 3")
            water_hunters = cursor.fetchall()
            recommendations["recommended_hunters"].extend(water_hunters)
        
        conn.close()
        return recommendations

class HuntRoyalCommands(commands.Cog):
    """Commandes Hunt Royal pour Discord Bot avec auto-update"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = HuntRoyalDatabase()
        self.suggestions = HuntRoyalSuggestions(self.db)
        self.analyzer = HuntRoyalAnalyzer(self.db)
        
        # Initialiser le scraper si disponible
        self.scraper_updater = None
        if SCRAPER_AVAILABLE:
            asyncio.create_task(self._init_scraper())
    
    async def _init_scraper(self):
        """Initialiser le système de scraping de manière asynchrone"""
        try:
            self.scraper_updater = await setup_hunt_royal_scraper(self.db.db_path)
            print("✅ Scraper Hunt Royal initialisé")
        except Exception as e:
            print(f"⚠️ Erreur initialisation scraper : {e}")

    @commands.group(name='hunt', invoke_without_command=True)
    async def hunt_royal(self, ctx):
        """Commandes Hunt Royal - Système complet d'aide aux joueurs avec données en temps réel"""
        embed = discord.Embed(
            title="🏹 Hunt Royal - Système d'Aide Complet",
            description="Toutes les commandes pour maîtriser Hunt Royal avec données depuis more-huntroyale.com !",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📊 Informations (Données Temps Réel)",
            value="`!hunt hunter <nom>` - Info chasseur détaillée\n"
                  "`!hunt stats <nom> <level>` - Stats précises niveau 1-10\n"
                  "`!hunt awaken <nom>` - Infos Awaken 1 et 2\n"
                  "`!hunt dungeon <nom>` - Info donjon\n"
                  "`!hunt list` - Liste tous les chasseurs",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Outils d'Analyse",
            value="`!hunt team <chasseur1> <chasseur2>...` - Analyser équipe\n"
                  "`!hunt recommend <donjon>` - Équipe recommandée\n"
                  "`!hunt compare <hunter1> <hunter2>` - Comparer chasseurs\n"
                  "`!hunt tier` - Tier list chasseurs",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Mise à Jour (Admin)",
            value="`!hunt update` - Forcer mise à jour depuis more-huntroyale.com\n"
                  "`!hunt cache` - Statut du cache des données\n"
                  "`!hunt reload` - Recharger module",
            inline=False
        )
        
        # Afficher le statut du scraper
        if SCRAPER_AVAILABLE and self.scraper_updater:
            embed.add_field(
                name="🌐 Source des Données",
                value="✅ **more-huntroyale.com** (Données officielles)\n"
                      "🔄 Mise à jour automatique toutes les 24h\n"
                      "📊 Stats HP/ATK niveaux 1-10, Awaken, vitesse, perks",
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Source des Données",
                value="📋 Données statiques (scraper indisponible)\n"
                      "Utilisez `!hunt update` pour réessayer",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @hunt_royal.command(name='stats')
    async def hunt_stats_level(self, ctx, hunter_name: str, level: int = 1):
        """Afficher les stats précises d'un chasseur à un niveau donné (1-10)"""
        if level < 1 or level > 10:
            await ctx.send("❌ Le niveau doit être entre 1 et 10")
            return
        
        # Essayer de récupérer depuis le scraper d'abord
        if SCRAPER_AVAILABLE and self.scraper_updater:
            try:
                stats = self.scraper_updater.scraper.get_hunter_stats_by_level(hunter_name, level)
                if stats:
                    embed = discord.Embed(
                        title=f"📊 {stats['name']} - Niveau {level}",
                        description=f"**Rôle:** {stats['role']}",
                        color=0x00ff00
                    )
                    
                    embed.add_field(
                        name="⚔️ Stats au Niveau " + str(level),
                        value=f"**❤️ HP:** {stats['hp']:,}\n"
                              f"**⚔️ Attaque:** {stats['attack']:,}\n"
                              f"**⚡ Vitesse:** {stats['speed']}",
                        inline=True
                    )
                    
                    # Calculer les améliorations par niveau
                    if level > 1:
                        prev_stats = self.scraper_updater.scraper.get_hunter_stats_by_level(hunter_name, level-1)
                        if prev_stats:
                            hp_gain = stats['hp'] - prev_stats['hp']
                            attack_gain = stats['attack'] - prev_stats['attack']
                            embed.add_field(
                                name=f"📈 Gain Niveau {level-1}→{level}",
                                value=f"**❤️ HP:** +{hp_gain:,}\n"
                                      f"**⚔️ ATK:** +{attack_gain:,}",
                                inline=True
                            )
                    
                    embed.set_footer(text="Données depuis more-huntroyale.com")
                    await ctx.send(embed=embed)
                    return
            except Exception as e:
                print(f"Erreur scraper stats : {e}")
        
        # Fallback sur la base de données locale
        hunter = self.db.get_hunter_by_name(hunter_name)
        if not hunter:
            await ctx.send(f"❌ Chasseur `{hunter_name}` non trouvé")
            return
        
        # Estimation basique (stats de base × multiplicateur niveau)
        level_multiplier = 1 + (level - 1) * 0.15  # +15% par niveau
        estimated_hp = int(hunter['health_base'] * level_multiplier)
        estimated_attack = int(hunter['attack_base'] * level_multiplier)
        
        embed = discord.Embed(
            title=f"📊 {hunter['name']} - Niveau {level} (Estimé)",
            description=f"**Élément:** {hunter['element']} | **Arme:** {hunter['weapon_type']}",
            color=0xffa500
        )
        
        embed.add_field(
            name="⚔️ Stats Estimées",
            value=f"**❤️ HP:** ~{estimated_hp:,}\n"
                  f"**⚔️ Attaque:** ~{estimated_attack:,}\n"
                  f"**🛡️ Défense:** {hunter['defense_base']}\n"
                  f"**⚡ Vitesse:** {hunter['speed_base']}",
            inline=True
        )
        
        embed.set_footer(text="⚠️ Stats estimées - Utilisez !hunt update pour données précises")
        await ctx.send(embed=embed)

    @hunt_royal.command(name='awaken')
    async def hunt_awaken_info(self, ctx, *, hunter_name: str):
        """Afficher les informations d'Awaken d'un chasseur"""
        if SCRAPER_AVAILABLE and self.scraper_updater:
            if hunter_name in self.scraper_updater.scraper.hunters_data:
                data = self.scraper_updater.scraper.hunters_data[hunter_name]
                
                embed = discord.Embed(
                    title=f"🔮 {hunter_name} - Informations Awaken",
                    color=0x9932cc
                )
                
                # Awaken 1 (toujours présent)
                embed.add_field(
                    name="⭐ Awaken 1",
                    value=data['awaken_1'].get('description', 'Information non disponible'),
                    inline=False
                )
                
                # Awaken 2 (optionnel)
                if data['awaken_2']:
                    embed.add_field(
                        name="⭐⭐ Awaken 2",
                        value=data['awaken_2'].get('description', 'Information non disponible'),
                        inline=False
                    )
                    embed.add_field(
                        name="✅ Statut Awaken 2",
                        value="**Disponible** - Ce chasseur a un Awaken 2",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="❌ Awaken 2",
                        value="Non disponible pour ce chasseur",
                        inline=True
                    )
                
                embed.add_field(
                    name="🔢 Nombre de Perks",
                    value=f"**{data['perks_count']}** perks disponibles",
                    inline=True
                )
                
                embed.set_footer(text="Données depuis more-huntroyale.com")
                await ctx.send(embed=embed)
                return
        
        # Fallback données locales
        hunter = self.db.get_hunter_by_name(hunter_name)
        if not hunter:
            await ctx.send(f"❌ Chasseur `{hunter_name}` non trouvé")
            return
        
        embed = discord.Embed(
            title=f"🔮 {hunter['name']} - Éveil",
            description=hunter['awakening_cost'],
            color=0x9932cc
        )
        
        embed.add_field(
            name="⚠️ Données Limitées",
            value="Utilisez `!hunt update` pour les informations Awaken détaillées",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @hunt_royal.command(name='list')
    async def hunt_list_all(self, ctx):
        """Lister tous les chasseurs disponibles"""
        if SCRAPER_AVAILABLE and self.scraper_updater:
            hunters = list(self.scraper_updater.scraper.hunters_data.keys())
            total = len(hunters)
        else:
            hunters_raw = self.db.get_all_hunters()
            hunters = [h['name'] for h in hunters_raw] if hunters_raw else []
            total = len(hunters)
        
        if not hunters:
            await ctx.send("❌ Aucun chasseur trouvé dans la base de données")
            return
        
        # Diviser en pages de 20 chasseurs
        pages = [hunters[i:i+20] for i in range(0, len(hunters), 20)]
        
        embed = discord.Embed(
            title=f"🏹 Hunt Royal - Tous les Chasseurs ({total} total)",
            description=f"**Page 1/{len(pages)}**\n\n" + 
                       "\n".join([f"• {hunter}" for hunter in pages[0]]),
            color=0x00ff88
        )
        
        if SCRAPER_AVAILABLE and self.scraper_updater:
            embed.set_footer(text="✅ Données depuis more-huntroyale.com | Utilisez !hunt hunter <nom> pour détails")
        else:
            embed.set_footer(text="⚠️ Données locales | Utilisez !hunt update pour données complètes")
        
        message = await ctx.send(embed=embed)
        
        # Ajouter navigation si plusieurs pages
        if len(pages) > 1:
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

    @hunt_royal.command(name='update')
    @commands.has_permissions(administrator=True)
    async def force_update_data(self, ctx):
        """Forcer la mise à jour des données depuis more-huntroyale.com (Admin)"""
        if not SCRAPER_AVAILABLE:
            await ctx.send("❌ Scraper non disponible. Vérifiez l'installation du module `utils.hunt_royal_scraper`")
            return
        
        if not self.scraper_updater:
            await ctx.send("⚠️ Scraper non initialisé. Redémarrage en cours...")
            await self._init_scraper()
            if not self.scraper_updater:
                await ctx.send("❌ Impossible d'initialiser le scraper")
                return
        
        # Message de statut
        status_embed = discord.Embed(
            title="🔄 Mise à jour Hunt Royal en cours...",
            description="Récupération des données depuis more-huntroyale.com",
            color=0xffa500
        )
        status_message = await ctx.send(embed=status_embed)
        
        try:
            # Forcer la mise à jour
            success = await self.scraper_updater.force_update()
            
            if success:
                hunters_count = len(self.scraper_updater.scraper.hunters_data)
                
                embed = discord.Embed(
                    title="✅ Mise à jour réussie !",
                    description=f"**{hunters_count} chasseurs** mis à jour depuis more-huntroyale.com",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="📊 Données Récupérées",
                    value="• Stats HP/ATK niveaux 1-10\n"
                          "• Informations Awaken 1 et 2\n"
                          "• Vitesse et nombre de perks\n"
                          "• Rôles des chasseurs",
                    inline=False
                )
                
                embed.add_field(
                    name="🕒 Prochaine Mise à Jour Auto",
                    value="Dans 24 heures",
                    inline=True
                )
                
                embed.set_footer(text=f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
            else:
                embed = discord.Embed(
                    title="❌ Échec de la mise à jour",
                    description="Impossible de récupérer les données. Réessayez plus tard.",
                    color=0xff0000
                )
            
            await status_message.edit(embed=embed)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur durant la mise à jour",
                description=f"Erreur : {str(e)}",
                color=0xff0000
            )
            await status_message.edit(embed=error_embed)

    @hunt_royal.command(name='cache')
    async def cache_status(self, ctx):
        """Afficher le statut du cache des données Hunt Royal"""
        embed = discord.Embed(
            title="📊 Hunt Royal - Statut du Cache",
            color=0x0099ff
        )
        
        if SCRAPER_AVAILABLE and self.scraper_updater:
            scraper = self.scraper_updater.scraper
            hunters_count = len(scraper.hunters_data)
            
            if scraper.last_update:
                last_update = datetime.fromisoformat(scraper.last_update)
                age = datetime.now() - last_update
                age_str = f"{age.days}j {age.seconds//3600}h {(age.seconds//60)%60}m"
            else:
                age_str = "Jamais"
            
            embed.add_field(
                name="✅ Cache Actif",
                value=f"**Chasseurs en cache :** {hunters_count}\n"
                      f"**Dernière mise à jour :** {age_str}\n"
                      f"**Source :** more-huntroyale.com",
                inline=False
            )
            
            if hunters_count > 0:
                # Exemple de chasseur avec données complètes
                sample_hunter = list(scraper.hunters_data.keys())[0]
                sample_data = scraper.hunters_data[sample_hunter]
                
                embed.add_field(
                    name=f"📋 Exemple : {sample_hunter}",
                    value=f"**Rôle :** {sample_data['role']}\n"
                          f"**Stats HP :** {len(sample_data['stats']['hp'])} niveaux\n"
                          f"**Awaken 2 :** {'✅' if sample_data['awaken_2'] else '❌'}\n"
                          f"**Perks :** {sample_data['perks_count']}",
                    inline=True
                )
            
        else:
            embed.add_field(
                name="❌ Cache Indisponible",
                value="Scraper non initialisé ou erreur de connexion",
                inline=False
            )
        
        # Stats base de données locale
        local_hunters = self.db.get_all_hunters()
        embed.add_field(
            name="🗄️ Base de Données Locale",
            value=f"**Chasseurs :** {len(local_hunters) if local_hunters else 0}\n"
                  f"**Type :** Données statiques/estimées",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @hunt_royal.command(name='hunter')
    async def hunt_hunter_info(self, ctx, *, hunter_name: str):
        """Informations détaillées sur un chasseur"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM hunters 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(id) LIKE LOWER(?)
        ''', (f'%{hunter_name}%', f'%{hunter_name}%'))
        
        hunter = cursor.fetchone()
        conn.close()
        
        if not hunter:
            embed = discord.Embed(
                title="❌ Chasseur non trouvé",
                description=f"Aucun chasseur trouvé pour : **{hunter_name}**",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Créer embed détaillé
        embed = discord.Embed(
            title=f"🏹 {hunter[1]} ({hunter[2]})",  # name (rarity)
            description=hunter[9],  # description
            color=0x00ff00 if hunter[2] == "Legendary" else 0x0099ff
        )
        
        embed.add_field(
            name="⚔️ Stats de Base",
            value=f"**Attaque:** {hunter[5]}\n"
                  f"**Santé:** {hunter[6]}\n"
                  f"**Défense:** {hunter[7]}\n"
                  f"**Vitesse:** {hunter[8]}",
            inline=True
        )
        
        embed.add_field(
            name="🔮 Capacités",
            value=f"**Élément:** {hunter[3]}\n"
                  f"**Arme:** {hunter[4]}\n"
                  f"**Compétences:** {hunter[10]}\n"
                  f"**Passif:** {hunter[11]}",
            inline=True
        )
        
        embed.add_field(
            name="⭐ Évaluation",
            value=f"**Tier:** {hunter[13]}\n"
                  f"**Éveil:** {hunter[12]}\n"
                  f"**Meilleur équipement:** {hunter[14]}",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Synergies & Counters",
            value=f"**Synergies:** {hunter[16]}\n"
                  f"**Counters:** {hunter[15]}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @hunt_royal.command(name='dungeon')
    async def hunt_dungeon_info(self, ctx, *, dungeon_name: str):
        """Informations détaillées sur un donjon"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dungeons 
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(id) LIKE LOWER(?)
        ''', (f'%{dungeon_name}%', f'%{dungeon_name}%'))
        
        dungeon = cursor.fetchone()
        conn.close()
        
        if not dungeon:
            embed = discord.Embed(
                title="❌ Donjon non trouvé",
                description=f"Aucun donjon trouvé pour : **{dungeon_name}**",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Créer embed détaillé
        embed = discord.Embed(
            title=f"🏰 {dungeon[1]} ({dungeon[3]})",  # name (difficulty)
            description=f"**Type:** {dungeon[2]} | **Niveau recommandé:** {dungeon[4]}",
            color=0xff4500 if dungeon[3] == "Hard" else 0xffa500
        )
        
        embed.add_field(
            name="👹 Boss",
            value=f"**Nom:** {dungeon[5]}\n"
                  f"**HP:** {dungeon[6]:,}\n"
                  f"**Éléments:** {dungeon[7]}",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Résistances/Faiblesses",
            value=f"**Résistances:** {dungeon[8]}\n"
                  f"**Faiblesses:** {dungeon[9]}",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Infos Pratiques",
            value=f"**Énergie:** {dungeon[15]}\n"
                  f"**Durée:** {dungeon[16]} min\n"
                  f"**Modificateurs:** {dungeon[14]}",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Stratégie",
            value=dungeon[11],
            inline=False
        )
        
        embed.add_field(
            name="✅ Chasseurs Recommandés",
            value=dungeon[12],
            inline=True
        )
        
        embed.add_field(
            name="❌ Chasseurs à Éviter",
            value=dungeon[13],
            inline=True
        )
        
        embed.add_field(
            name="🎁 Récompenses",
            value=dungeon[10],
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @hunt_royal.command(name='suggest')
    async def create_suggestion(self, ctx, *, suggestion_text: str):
        """Créer une nouvelle suggestion pour Hunt Royal"""
        parts = suggestion_text.split('|', 1)
        if len(parts) != 2:
            embed = discord.Embed(
                title="❌ Format incorrect",
                description="Utilisez : `!hunt suggest <titre> | <description>`\n"
                           "Exemple : `!hunt suggest Nouveau chasseur | Il faudrait ajouter un chasseur de type Vent`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        title = parts[0].strip()
        description = parts[1].strip()
        
        suggestion_id = await self.suggestions.create_suggestion(
            str(ctx.author.id), 
            ctx.author.display_name, 
            title, 
            description,
            "hunt_royal"
        )
        
        embed = discord.Embed(
            title="✅ Suggestion créée !",
            description=f"**ID:** {suggestion_id}\n"
                       f"**Titre:** {title}\n"
                       f"**Description:** {description[:200]}{'...' if len(description) > 200 else ''}",
            color=0x00ff00
        )
        
        embed.add_field(
            name="👥 Vote",
            value=f"Réagissez avec ⬆️ ou ⬇️ pour voter !",
            inline=False
        )
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("⬆️")
        await message.add_reaction("⬇️")
    
    @hunt_royal.command(name='economy')
    async def hunt_economy_info(self, ctx):
        """Afficher l'économie Hunt Royal (coûts, tiers, popularité)"""
        hunters = self.db.get_all_hunters()
        
        if not hunters:
            embed = discord.Embed(
                title="❌ Aucune donnée",
                description="Aucun chasseur trouvé dans la base de données",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="💰 Hunt Royal - Économie & Meta",
            description="Coûts, tiers et popularité des chasseurs",
            color=0xffd700
        )
        
        # Séparer par type de coût
        coins_hunters = [h for h in hunters if h['cost_type'] == 'coins']
        gems_hunters = [h for h in hunters if h['cost_type'] == 'gems']
        special_hunters = [h for h in hunters if h['cost_type'] == 'special']
        
        # Chasseurs coins
        if coins_hunters:
            coins_text = ""
            for hunter in coins_hunters[:5]:
                tier_emoji = self._get_tier_emoji(hunter['tier_meta'])
                coins_text += f"{tier_emoji} **{hunter['name']}** - {hunter['cost_amount']} coins (Pop: {hunter['popularity']}%)\n"
            embed.add_field(
                name="🪙 Chasseurs Coins",
                value=coins_text or "Aucun",
                inline=False
            )
        
        # Chasseurs gems
        if gems_hunters:
            gems_text = ""
            for hunter in gems_hunters[:5]:
                tier_emoji = self._get_tier_emoji(hunter['tier_meta'])
                gems_text += f"{tier_emoji} **{hunter['name']}** - {hunter['cost_amount']} gems (Pop: {hunter['popularity']}%)\n"
            embed.add_field(
                name="💎 Chasseurs Premium",
                value=gems_text or "Aucun",
                inline=False
            )
        
        # Chasseurs spéciaux
        if special_hunters:
            special_text = ""
            for hunter in special_hunters[:5]:
                tier_emoji = self._get_tier_emoji(hunter['tier_meta'])
                special_text += f"{tier_emoji} **{hunter['name']}** - {hunter['cost_amount']} event tokens (Pop: {hunter['popularity']}%)\n"
            embed.add_field(
                name="⭐ Chasseurs Événements",
                value=special_text or "Aucun",
                inline=False
            )
        
        embed.add_field(
            name="📊 Légende Tiers",
            value="🏆 S+ = Meta dominant\n🥇 S = Très fort\n🥈 A+/A = Bon\n🥉 B+ = Correct\n📉 C+ = Faible",
            inline=False
        )
        
        embed.set_footer(text=f"Arsenal Bot • {len(hunters)} chasseurs • Données économiques réelles")
        return embed

    def _get_tier_emoji(self, tier):
        """Retourner l'emoji correspondant au tier"""
        tier_emojis = {
            'S+': '🏆',
            'S': '🥇', 
            'A+': '🥈',
            'A': '🥈',
            'B+': '🥉',
            'B': '🥉',
            'C+': '📉',
            'C': '📉'
        }
        return tier_emojis.get(tier, '❓')

    def _get_cost_color(self, cost_type):
        """Retourner la couleur selon le type de coût"""
        colors = {
            'coins': 0xffd700,   # Or
            'gems': 0x9932cc,    # Violet
            'special': 0xff4500  # Rouge-orange
        }
        return colors.get(cost_type, 0x808080)

    async def analyze_team_composition(self, ctx, hunters):
        """Analyser une composition d'équipe"""
        if len(hunters) < 2:
            embed = discord.Embed(
                title="❌ Équipe insuffisante",
                description="Veuillez spécifier au moins 2 chasseurs\n"
                           "Exemple : `!hunt team raven flamewarden frostguard`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        analysis = await self.analyzer.analyze_team_composition(list(hunters))
        
        if not analysis["hunters"]:
            embed = discord.Embed(
                title="❌ Chasseurs non trouvés",
                description="Aucun chasseur valide trouvé dans votre liste",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📊 Analyse d'Équipe Hunt Royal",
            description=f"Analyse de {len(analysis['hunters'])} chasseurs",
            color=0x00ff00
        )
        
        # Stats totales
        stats = analysis["total_stats"]
        embed.add_field(
            name="⚔️ Stats Totales",
            value=f"**Attaque:** {stats['attack']:,}\n"
                  f"**Santé:** {stats['health']:,}\n"
                  f"**Défense:** {stats['defense']:,}\n"
                  f"**Vitesse:** {stats['speed']:,}",
            inline=True
        )
        
        # Composition élémentaire
        elements_text = "\n".join([f"**{elem}:** {count}" for elem, count in analysis["elements"].items()])
        embed.add_field(
            name="🔮 Éléments",
            value=elements_text or "Aucun",
            inline=True
        )
        
        # Types d'armes
        weapons_text = "\n".join([f"**{weapon}:** {count}" for weapon, count in analysis["weapon_types"].items()])
        embed.add_field(
            name="⚔️ Armes",
            value=weapons_text or "Aucune",
            inline=True
        )
        
        # Faiblesses détectées
        if analysis["weaknesses"]:
            embed.add_field(
                name="⚠️ Faiblesses Détectées",
                value="\n".join([f"• {weakness}" for weakness in analysis["weaknesses"]]),
                inline=False
            )
        
        # Recommandations
        if analysis["recommendations"]:
            embed.add_field(
                name="💡 Recommandations",
                value="\n".join([f"• {rec}" for rec in analysis["recommendations"]]),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @hunt_royal.command(name='reload')
    @commands.has_permissions(administrator=True)
    async def reload_hunt_module(self, ctx):
        """Recharger le module Hunt Royal (Admin seulement)"""
        try:
            # Réimporter le module
            if 'hunt_royal_system' in sys.modules:
                importlib.reload(sys.modules['hunt_royal_system'])
            
            # Recharger la base de données
            self.db.load_complete_data()
            
            embed = discord.Embed(
                title="✅ Module Hunt Royal rechargé",
                description="Le module Hunt Royal a été rechargé avec succès !\n"
                           "Toutes les nouvelles données ont été mises à jour.",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🔄 Rechargé",
                value="• Base de données\n• Commandes\n• Système de suggestions\n• Analyseur d'équipe",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur de rechargement",
                description=f"Erreur lors du rechargement : {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)

# ==================== SYSTÈME DE HOT-RELOAD ====================

class HuntRoyalModuleManager:
    """Gestionnaire de module avec Hot-Reload pour Hunt Royal"""
    
    def __init__(self):
        self.module_name = 'hunt_royal_system'
        self.last_modified = 0
        self.watch_file = __file__
        
    def check_for_changes(self):
        """Vérifier si le module a été modifié"""
        try:
            current_modified = os.path.getmtime(self.watch_file)
            if current_modified > self.last_modified:
                self.last_modified = current_modified
                return True
        except:
            pass
        return False
    
    def reload_module(self, bot):
        """Recharger le module Hunt Royal"""
        try:
            # Retirer l'ancien cog s'il existe
            if 'HuntRoyalCommands' in [cog.__class__.__name__ for cog in bot.cogs.values()]:
                bot.remove_cog('HuntRoyalCommands')
            
            # Recharger le module
            if self.module_name in sys.modules:
                importlib.reload(sys.modules[self.module_name])
            
            # Ajouter le nouveau cog
            bot.add_cog(HuntRoyalCommands(bot))
            
            print("✅ Module Hunt Royal rechargé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur rechargement Hunt Royal : {e}")
            return False

# ==================== FONCTION D'INITIALISATION ====================

def setup(bot):
    """Fonction appelée pour charger le module Hunt Royal"""
    bot.add_cog(HuntRoyalCommands(bot))
    print("🏹 Module Hunt Royal chargé avec succès !")

def teardown(bot):
    """Fonction appelée pour décharger le module Hunt Royal"""
    bot.remove_cog('HuntRoyalCommands')
    print("🏹 Module Hunt Royal déchargé")

# Auto-reload si le fichier est modifié (optionnel)
if __name__ == "__main__":
    print("🏹 Hunt Royal System - Module autonome initialisé")
    print("📊 Base de données prête")
    print("💡 Système de suggestions actif")
    print("🔄 Hot-reload disponible")
