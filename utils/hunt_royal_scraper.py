"""
🏹 HUNT ROYAL DATA SCRAPER - Arsenal Bot V4
=============================================

Système de récupération automatique des données Hunt Royal depuis more-huntroyale.com
- Récupération des stats HP/ATK niveau 1-10
- Informations sur les Awaken 1 et 2
- Vitesse et nombre de perks
- Mise à jour automatique de la base de données

Hook intelligent avec cache et détection de changements
"""

import requests
import re
import json
import sqlite3
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from datetime import datetime, timedelta
import time

class HuntRoyalScraper:
    """Scraper intelligent pour récupérer les données Hunt Royal"""
    
    def __init__(self):
        self.base_url = "https://more-huntroyale.com"
        self.hunters_url = f"{self.base_url}/public/hunters.html"
        self.cache_file = "hunt_royal_cache.json"
        self.last_update = None
        self.hunters_data = {}
        
        # Headers pour éviter le blocage
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def fetch_hunters_list(self) -> List[str]:
        """Récupérer la liste de tous les chasseurs disponibles depuis more-huntroyale.com"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(self.hunters_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        hunters = []
                        
                        # Méthode 1: Extraire depuis les noms d'images
                        images = soup.find_all('img')
                        for img in images:
                            src = img.get('src', '')
                            if '/hunters/' in src and src.endswith('.png'):
                                # Extraire le nom du fichier : "ElfArcher.png" -> "Elf Archer"
                                filename = src.split('/')[-1].replace('.png', '')
                                # Convertir CamelCase en nom lisible
                                hunter_name = self._convert_filename_to_name(filename)
                                if hunter_name and hunter_name not in hunters:
                                    hunters.append(hunter_name)
                        
                        # Méthode 2: Extraire depuis les titres h3 (backup)
                        if len(hunters) < 10:  # Si peu de résultats, essayer autre méthode
                            for h3 in soup.find_all('h3'):
                                hunter_name = h3.get_text().strip()
                                if hunter_name and len(hunter_name) > 2 and hunter_name not in hunters:
                                    # Filtrer les éléments non-chasseurs
                                    if not any(skip in hunter_name.lower() for skip in ['additional', 'links', 'menu', 'login']):
                                        hunters.append(hunter_name)
                        
                        # Nettoyer la liste
                        hunters = [h for h in hunters if h and len(h) > 2]
                        hunters.sort()
                        
                        print(f"✅ {len(hunters)} chasseurs trouvés sur more-huntroyale.com")
                        if len(hunters) > 0:
                            print(f"   Exemples: {', '.join(hunters[:5])}")
                        
                        return hunters
                    else:
                        print(f"❌ Erreur HTTP {response.status} lors de la récupération")
                        return []
                        
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des chasseurs : {e}")
            return []
    
    def _convert_filename_to_name(self, filename: str) -> str:
        """Convertir un nom de fichier CamelCase en nom lisible"""
        # Gérer les cas spéciaux connus
        special_cases = {
            'ElfArcher': 'Elf Archer',
            'DragonKnight': 'Dragon Knight',
            'SpiderQueen': 'Spider Queen',
            'ImpsMaster': 'Imp Master',
            'FrozenQueen': 'Frozen Queen',
            'AxeMaster': 'Axe Master',
            'CaptainHook': 'Captain Hook',
            'LifeStealer': 'Life Stealer',
            'RagingOrk': 'Raging Orc',
            'BoomBoom': 'Boom Boom',
            'GrayWolf': 'Gray Wolf',
            'MadDoctor': 'Mad Doctor',
            'AncientOne': 'Ancient One',
            'TheRipper': 'The Ripper',
            'GrimReaper': 'Grim Reaper',
            'SkullMaster': 'Skull Master',
            'PlagueDoctor': 'Plague Doctor',
            'VoidKnight': 'Void Knight',
            'MutantTurtle': 'Mutant Turtle',
            'PlagueRat': 'Plague Rat',
            'Werebear': 'WereBear',
            'GoblinEngineer': 'Goblin Engineer',
            'SunWukong': 'Sun Wukong',
            'Tikitiki': 'Tiki Tiki',
            'ApeLord': 'Ape Lord',
            'SirBarkalot': 'Sir Barkalot',
            'ApexPredator': 'Apex Predator',
            'ShadowWitch': 'Shadow Witch',
            'MechAssassin': 'Mech Assassin',
            'GirlWithGolem': 'A Girl And Her Golem',
            'CommanderVanellus': 'Commander Vanellus',
            'Killergirl': 'Killer Girl',
            'TimeTraveler': 'Time Traveler'
        }
        
        if filename in special_cases:
            return special_cases[filename]
        
        # Conversion générique CamelCase
        result = ''
        for i, char in enumerate(filename):
            if char.isupper() and i > 0:
                result += ' '
            result += char
        
        return result.strip()
    
    async def fetch_hunter_detailed_data(self, hunter_name: str) -> Optional[Dict]:
        """Récupérer les données détaillées d'un chasseur spécifique
        
        Cette méthode va essayer de trouver un endpoint API ou une page détaillée
        pour récupérer les stats niveau 1-10, awaken, etc.
        """
        try:
            # Essayer différentes approches pour récupérer les données
            
            # 1. Chercher une API JSON
            api_url = f"{self.base_url}/api/hunter/{hunter_name.lower().replace(' ', '-')}"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Essayer l'API JSON d'abord
                try:
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return await self._parse_api_data(data, hunter_name)
                except:
                    pass
                
                # 2. Chercher une page détaillée pour ce chasseur
                detail_url = f"{self.base_url}/hunter/{hunter_name.lower().replace(' ', '-')}"
                try:
                    async with session.get(detail_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            return await self._parse_hunter_page(html, hunter_name)
                except:
                    pass
                
                # 3. Chercher dans le JavaScript de la page principale
                async with session.get(self.hunters_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._extract_from_main_page(html, hunter_name)
                        
        except Exception as e:
            print(f"❌ Erreur récupération données {hunter_name} : {e}")
            
        return None
    
    async def _parse_api_data(self, data: Dict, hunter_name: str) -> Dict:
        """Parser les données depuis une API JSON"""
        hunter_data = {
            "name": hunter_name,
            "role": data.get("role", "Unknown"),
            "stats": {
                "hp": data.get("hp_stats", []),
                "attack": data.get("attack_stats", []),
                "speed": data.get("speed", 0)
            },
            "perks_count": data.get("perks_count", 0),
            "awaken_1": data.get("awaken_1", {}),
            "awaken_2": data.get("awaken_2", None),
            "image_url": data.get("image_url", f"{self.base_url}/assets/images/hunters/{hunter_name.replace(' ', '')}.png"),
            "last_updated": datetime.now().isoformat()
        }
        
        return hunter_data
    
    async def _parse_hunter_page(self, html: str, hunter_name: str) -> Dict:
        """Parser une page détaillée de chasseur"""
        soup = BeautifulSoup(html, 'html.parser')
        
        hunter_data = {
            "name": hunter_name,
            "role": "Unknown",
            "stats": {"hp": [], "attack": [], "speed": 0},
            "perks_count": 0,
            "awaken_1": {},
            "awaken_2": None,
            "image_url": f"{self.base_url}/assets/images/hunters/{hunter_name.replace(' ', '')}.png",
            "last_updated": datetime.now().isoformat()
        }
        
        # Chercher les stats dans des tableaux ou divs
        stats_tables = soup.find_all('table')
        for table in stats_tables:
            # Essayer d'extraire HP/ATK par niveau
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    # Structure probable : Level | HP | ATK
                    try:
                        level = cells[0].get_text().strip()
                        hp = cells[1].get_text().strip()
                        attack = cells[2].get_text().strip()
                        
                        if level.isdigit() and hp.isdigit() and attack.isdigit():
                            hunter_data["stats"]["hp"].append(int(hp))
                            hunter_data["stats"]["attack"].append(int(attack))
                    except:
                        continue
        
        return hunter_data
    
    async def _extract_from_main_page(self, html: str, hunter_name: str) -> Dict:
        """Extraire les données depuis la page principale (JavaScript/JSON embedded)"""
        # Chercher des données JSON dans le script
        soup = BeautifulSoup(html, 'html.parser')
        
        # Chercher dans les scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Chercher des patterns JSON
                json_patterns = [
                    r'hunters\s*[:=]\s*(\{.*?\}|\[.*?\])',
                    r'hunterData\s*[:=]\s*(\{.*?\}|\[.*?\])',
                    r'const\s+hunters\s*=\s*(\{.*?\}|\[.*?\])',
                    r'var\s+hunters\s*=\s*(\{.*?\}|\[.*?\])'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script.string, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            # Chercher notre chasseur dans les données
                            if isinstance(data, dict) and hunter_name in data:
                                return await self._parse_api_data(data[hunter_name], hunter_name)
                            elif isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict) and item.get('name') == hunter_name:
                                        return await self._parse_api_data(item, hunter_name)
                        except:
                            continue
        
        # Données par défaut si rien trouvé
        return {
            "name": hunter_name,
            "role": "Unknown",
            "stats": {"hp": [], "attack": [], "speed": 0},
            "perks_count": 0,
            "awaken_1": {"description": "Awaken 1 info not available"},
            "awaken_2": None,
            "image_url": f"{self.base_url}/assets/images/hunters/{hunter_name.replace(' ', '')}.png",
            "last_updated": datetime.now().isoformat(),
            "source": "scraped_basic"
        }
    
    async def fetch_all_hunters_data(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """Récupérer les données de tous les chasseurs avec cache intelligent"""
        
        # Vérifier le cache
        if not force_refresh and self._load_cache():
            cache_age = datetime.now() - datetime.fromisoformat(self.last_update)
            if cache_age < timedelta(hours=24):  # Cache valide 24h
                print(f"✅ Cache valide ({len(self.hunters_data)} chasseurs), utilisé")
                return self.hunters_data
        
        print("🔄 Récupération des données Hunt Royal depuis more-huntroyale.com...")
        
        # Récupérer la liste des chasseurs
        hunters_list = await self.fetch_hunters_list()
        if not hunters_list:
            print("❌ Impossible de récupérer la liste des chasseurs")
            return {}
        
        # Récupérer les données détaillées (avec limitation de débit)
        all_hunters_data = {}
        for i, hunter_name in enumerate(hunters_list):
            print(f"📥 Récupération {hunter_name} ({i+1}/{len(hunters_list)})")
            
            hunter_data = await self.fetch_hunter_detailed_data(hunter_name)
            if hunter_data:
                all_hunters_data[hunter_name] = hunter_data
            
            # Pause pour éviter la surcharge du serveur
            await asyncio.sleep(0.5)
        
        # Sauvegarder le cache
        self.hunters_data = all_hunters_data
        self.last_update = datetime.now().isoformat()
        self._save_cache()
        
        print(f"✅ {len(all_hunters_data)} chasseurs récupérés et mis en cache")
        return all_hunters_data
    
    def _load_cache(self) -> bool:
        """Charger le cache depuis le fichier"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                self.hunters_data = cache_data.get('hunters_data', {})
                self.last_update = cache_data.get('last_update')
                return True
        except:
            return False
    
    def _save_cache(self):
        """Sauvegarder le cache dans un fichier"""
        try:
            cache_data = {
                'hunters_data': self.hunters_data,
                'last_update': self.last_update
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde cache : {e}")
    
    async def update_database(self, db_path: str = "hunt_royal.db"):
        """Mettre à jour la base de données avec les nouvelles données"""
        hunters_data = await self.fetch_all_hunters_data()
        
        if not hunters_data:
            print("❌ Aucune donnée à mettre à jour")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer/mettre à jour la table avec les nouvelles colonnes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunters_detailed (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT,
                hp_level_1 INTEGER,
                hp_level_2 INTEGER,
                hp_level_3 INTEGER,
                hp_level_4 INTEGER,
                hp_level_5 INTEGER,
                hp_level_6 INTEGER,
                hp_level_7 INTEGER,
                hp_level_8 INTEGER,
                hp_level_9 INTEGER,
                hp_level_10 INTEGER,
                attack_level_1 INTEGER,
                attack_level_2 INTEGER,
                attack_level_3 INTEGER,
                attack_level_4 INTEGER,
                attack_level_5 INTEGER,
                attack_level_6 INTEGER,
                attack_level_7 INTEGER,
                attack_level_8 INTEGER,
                attack_level_9 INTEGER,
                attack_level_10 INTEGER,
                speed INTEGER,
                perks_count INTEGER,
                awaken_1_description TEXT,
                awaken_2_description TEXT,
                has_awaken_2 BOOLEAN,
                image_url TEXT,
                source TEXT,
                last_updated TEXT
            )
        ''')
        
        # Insérer/mettre à jour les données
        updated_count = 0
        for hunter_name, data in hunters_data.items():
            hunter_id = hunter_name.lower().replace(' ', '_')
            
            # Préparer les stats HP (10 niveaux)
            hp_stats = data['stats']['hp'][:10] + [0] * (10 - len(data['stats']['hp'][:10]))
            attack_stats = data['stats']['attack'][:10] + [0] * (10 - len(data['stats']['attack'][:10]))
            
            cursor.execute('''
                INSERT OR REPLACE INTO hunters_detailed VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                hunter_id, data['name'], data['role'],
                *hp_stats,  # HP niveaux 1-10
                *attack_stats,  # ATK niveaux 1-10
                data['stats']['speed'],
                data['perks_count'],
                data['awaken_1'].get('description', ''),
                data['awaken_2'].get('description', '') if data['awaken_2'] else '',
                bool(data['awaken_2']),
                data['image_url'],
                data.get('source', 'scraped'),
                data['last_updated']
            ))
            
            updated_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Base de données mise à jour : {updated_count} chasseurs")
    
    def get_hunter_stats_by_level(self, hunter_name: str, level: int) -> Optional[Dict]:
        """Récupérer les stats d'un chasseur à un niveau donné"""
        if hunter_name not in self.hunters_data:
            return None
        
        data = self.hunters_data[hunter_name]
        stats = data['stats']
        
        if level < 1 or level > 10:
            return None
        
        return {
            'name': hunter_name,
            'level': level,
            'hp': stats['hp'][level-1] if level-1 < len(stats['hp']) else 0,
            'attack': stats['attack'][level-1] if level-1 < len(stats['attack']) else 0,
            'speed': stats['speed'],
            'role': data['role']
        }

# ==================== HOOK D'INTÉGRATION ====================

class HuntRoyalAutoUpdater:
    """Système d'auto-update pour intégrer le scraper au bot"""
    
    def __init__(self, scraper: HuntRoyalScraper, db_path: str = "hunt_royal.db"):
        self.scraper = scraper
        self.db_path = db_path
        self.auto_update_interval = 24 * 60 * 60  # 24 heures
        self.last_auto_update = None
    
    async def check_and_update(self) -> bool:
        """Vérifier si une mise à jour est nécessaire et l'effectuer"""
        now = datetime.now()
        
        if self.last_auto_update:
            time_since_update = now - self.last_auto_update
            if time_since_update.total_seconds() < self.auto_update_interval:
                return False  # Pas encore temps de mettre à jour
        
        print("🔄 Mise à jour automatique Hunt Royal...")
        await self.scraper.update_database(self.db_path)
        self.last_auto_update = now
        return True
    
    async def force_update(self) -> bool:
        """Forcer une mise à jour immédiate"""
        print("🔄 Mise à jour forcée Hunt Royal...")
        await self.scraper.update_database(self.db_path)
        self.last_auto_update = datetime.now()
        return True

# ==================== FONCTION D'EXPORTATION ====================

async def setup_hunt_royal_scraper(db_path: str = "hunt_royal.db") -> HuntRoyalAutoUpdater:
    """Initialiser le système de scraping Hunt Royal"""
    scraper = HuntRoyalScraper()
    updater = HuntRoyalAutoUpdater(scraper, db_path)
    
    # Première mise à jour au démarrage
    await updater.check_and_update()
    
    return updater

# ==================== TEST ====================

if __name__ == "__main__":
    async def test_scraper():
        print("🧪 Test du scraper Hunt Royal")
        
        scraper = HuntRoyalScraper()
        
        # Tester la récupération de la liste
        hunters = await scraper.fetch_hunters_list()
        print(f"Chasseurs trouvés : {len(hunters)}")
        
        if hunters:
            # Tester sur les 3 premiers chasseurs
            for hunter in hunters[:3]:
                print(f"\n📊 Test données pour {hunter}...")
                data = await scraper.fetch_hunter_detailed_data(hunter)
                if data:
                    print(f"✅ Données récupérées pour {hunter}")
                    print(f"   - Rôle: {data['role']}")
                    print(f"   - Stats HP: {len(data['stats']['hp'])} niveaux")
                    print(f"   - Stats ATK: {len(data['stats']['attack'])} niveaux")
                    print(f"   - Vitesse: {data['stats']['speed']}")
                    print(f"   - Perks: {data['perks_count']}")
                    print(f"   - Awaken 2: {'Oui' if data['awaken_2'] else 'Non'}")
                else:
                    print(f"❌ Échec récupération pour {hunter}")
        
        # Tester la mise à jour DB
        print(f"\n🗄️ Test mise à jour base de données...")
        await scraper.update_database("test_hunt_royal.db")
    
    asyncio.run(test_scraper())
