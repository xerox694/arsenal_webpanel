import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timezone
import json
import random
import os
import sys

# 📁 Chemin économie
ECONOMIE_PATH = "data/economie.json"

from typing import Any

def load_economie() -> dict[str, Any]:
    if os.path.exists(ECONOMIE_PATH):
        with open(ECONOMIE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_economie(data: dict[str, Any]):
    with open(ECONOMIE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_balance(user_id: str, eco_data: dict[str, Any]) -> int:
    return eco_data.get(str(user_id), {}).get("balance", 0)

def update_balance(user_id: str, amount: int, eco_data: dict[str, Any], jeu: str = ""):
    uid = str(user_id)
    eco_data.setdefault(uid, {"balance": 0, "history": []})
    eco_data[uid]["balance"] += amount
    eco_data[uid]["history"].append({
        "jeu": jeu,
        "gain": amount,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    })
    save_economie(eco_data)

def get_leaderboard(eco_data: dict[str, Any]) -> list[tuple[str, int]]:
    sorted_data = sorted(eco_data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)
    return [(uid, data["balance"]) for uid, data in sorted_data[:5]]

def get_history(user_id: str, eco_data: dict[str, Any]) -> list[dict[str, Any]]:
    uid = str(user_id)
    history = eco_data.get(uid, {}).get("history", [])
    return history[-10:]
# ...existing code...
class ArsenalCreatorPanel(tk.Tk):
    def __init__(self, bot: Any):
        super().__init__()
        self.bot = bot
        self.title("👑 Arsenal Creator Studio - v3.5")
        self.geometry("1100x700")
        self.configure(bg="#101820")
        self.sidebar = tk.Frame(self, bg="#2c2c2c", width=190)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg="#1e1e1e")
        self.content.pack(side="right", expand=True, fill="both")
        self.active_tab = None
        self.bet_var = tk.StringVar(value="500")
        self.sidebar_btn = None
        self.build_sidebar()
        self.load_dashboard()
        # ...toutes tes listes de composants ici...
# ...existing code...

    def load_reel_pocket(self):
        self.clear_content()
        self.active_tab = "reel_pocket"
        tk.Label(self.content, text="🎲 Reel Pocket (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Reel Pocket n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

        self.sidebar = tk.Frame(self, bg="#2c2c2c", width=190)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self, bg="#1e1e1e")
        self.content.pack(side="right", expand=True, fill="both")

        self.active_tab = None
        self.bet_var = tk.StringVar(value="500")
        self.sidebar_btn = None  # Ensure sidebar_btn attribute exists
        self.build_sidebar()
        self.load_dashboard()

        # Configuration PC par défaut
        self.pc_config: dict[str, dict[str, str]] = {
            "Boîtier": {"modèle": "NZXT H510", "marque": "NZXT", "format": "ATX"},
            "Carte mère": {"modèle": "MSI B550 Tomahawk", "marque": "MSI", "socket": "AM4", "format": "ATX"},
            "CPU": {"modèle": "Ryzen 5 5600X", "marque": "AMD", "socket": "AM4", "coeurs": "6", "freq": "4.6GHz"},
            "GPU": {"modèle": "RTX 3060", "marque": "NVIDIA", "VRAM": "12Go"},
            "RAM": {"modèle": "Corsair Vengeance", "type": "DDR4", "taille": "16Go", "freq": "3200MHz"},
            "Stockage": {"modèle": "Samsung 970 EVO", "type": "NVMe", "taille": "1To"},
            "Alim": {"modèle": "Corsair RM650x", "puissance": "650W", "certif": "Gold"},
            "Ventilateur": {"modèle": "Noctua NF-A12", "type": "Air", "diamètre": "120mm"},
            "Refroidissement": {"modèle": "Cooler Master Hyper 212", "type": "Air", "compatibilité": "AM4/1151"}
        }
        self.pc_score = 0

        self.boitiers = [
            # 5 bas de gamme
            {"modèle": "Sharkoon VS4", "marque": "Sharkoon", "format": "ATX"},
            {"modèle": "Aerocool Bolt Mini", "marque": "Aerocool", "format": "mATX"},
            {"modèle": "Zalman Z1 Neo", "marque": "Zalman", "format": "ATX"},
            {"modèle": "BitFenix Nova", "marque": "BitFenix", "format": "ATX"},
            {"modèle": "Thermaltake V200", "marque": "Thermaltake", "format": "ATX"},
            # 5 milieu de gamme
            {"modèle": "NZXT H510", "marque": "NZXT", "format": "ATX"},
            {"modèle": "Corsair 4000D", "marque": "Corsair", "format": "ATX"},
            {"modèle": "Cooler Master NR600", "marque": "Cooler Master", "format": "ATX"},
            {"modèle": "Phanteks Eclipse P400A", "marque": "Phanteks", "format": "ATX"},
            {"modèle": "SilverStone Fara R1", "marque": "SilverStone", "format": "ATX"},
            # 5 haut de gamme
            {"modèle": "Lian Li O11 Dynamic", "marque": "Lian Li", "format": "ATX"},
            {"modèle": "Be Quiet! Pure Base 500DX", "marque": "Be Quiet!", "format": "ATX"},
            {"modèle": "Fractal Meshify C", "marque": "Fractal", "format": "ATX"},
            {"modèle": "InWin 101", "marque": "InWin", "format": "ATX"},
            {"modèle": "Antec NX410", "marque": "Antec", "format": "ATX"}
        ]
        self.cartes_meres = [
            # 5 bas de gamme
            {"modèle": "ASRock B450M-HDV", "marque": "ASRock", "socket": "AM4", "format": "mATX"},
            {"modèle": "Gigabyte H310M", "marque": "Gigabyte", "socket": "LGA1151", "format": "mATX"},
            {"modèle": "MSI A320M-A PRO", "marque": "MSI", "socket": "AM4", "format": "mATX"},
            {"modèle": "ASUS PRIME B250M", "marque": "ASUS", "socket": "LGA1151", "format": "mATX"},
            {"modèle": "Biostar B250GT5", "marque": "Biostar", "socket": "LGA1151", "format": "ATX"},
            # 5 milieu de gamme
            {"modèle": "MSI B550 Tomahawk", "marque": "MSI", "socket": "AM4", "format": "ATX"},
            {"modèle": "ASUS Z690 Prime", "marque": "ASUS", "socket": "LGA1700", "format": "ATX"},
            {"modèle": "Gigabyte X570 Aorus", "marque": "Gigabyte", "socket": "AM4", "format": "ATX"},
            {"modèle": "ASRock B550 Steel Legend", "marque": "ASRock", "socket": "AM4", "format": "ATX"},
            {"modèle": "MSI MPG Z490 Gaming Plus", "marque": "MSI", "socket": "LGA1200", "format": "ATX"},
            # 5 haut de gamme
            {"modèle": "ASUS ROG Maximus XIII Hero", "marque": "ASUS", "socket": "LGA1200", "format": "ATX"},
            {"modèle": "Gigabyte Z690 Aorus Master", "marque": "Gigabyte", "socket": "LGA1700", "format": "ATX"},
            {"modèle": "MSI MEG X570 ACE", "marque": "MSI", "socket": "AM4", "format": "ATX"},
            {"modèle": "ASRock X570 Taichi", "marque": "ASRock", "socket": "AM4", "format": "ATX"},
            {"modèle": "ASUS ROG Crosshair VIII Hero", "marque": "ASUS", "socket": "AM4", "format": "ATX"}
        ]
        from typing import TypedDict, List

        class CPUInfo(TypedDict):
            modèle: str
            marque: str
            socket: str
            coeurs: int
            freq: str

        self.cpus: List[CPUInfo] = [
            # 5 bas de gamme
            {"modèle": "Intel Pentium G5400", "marque": "Intel", "socket": "LGA1151", "coeurs": 2, "freq": "3.7GHz"},
            {"modèle": "AMD Athlon 3000G", "marque": "AMD", "socket": "AM4", "coeurs": 2, "freq": "3.5GHz"},
            {"modèle": "Intel i3-9100F", "marque": "Intel", "socket": "LGA1151", "coeurs": 4, "freq": "4.2GHz"},
            {"modèle": "AMD Ryzen 3 3200G", "marque": "AMD", "socket": "AM4", "coeurs": 4, "freq": "4.0GHz"},
            {"modèle": "Intel i3-10100", "marque": "Intel", "socket": "LGA1200", "coeurs": 4, "freq": "4.3GHz"},
            # 5 milieu de gamme
            {"modèle": "Ryzen 5 5600X", "marque": "AMD", "socket": "AM4", "coeurs": 6, "freq": "4.6GHz"},
            {"modèle": "Intel i5-12400F", "marque": "Intel", "socket": "LGA1700", "coeurs": 6, "freq": "4.4GHz"},
            {"modèle": "Ryzen 7 5800X", "marque": "AMD", "socket": "AM4", "coeurs": 8, "freq": "4.7GHz"},
            {"modèle": "Intel i7-12700K", "marque": "Intel", "socket": "LGA1700", "coeurs": 12, "freq": "5.0GHz"},
            {"modèle": "Ryzen 5 7600X", "marque": "AMD", "socket": "AM5", "coeurs": 6, "freq": "5.3GHz"},
            # 5 haut de gamme
            {"modèle": "Intel i9-13900K", "marque": "Intel", "socket": "LGA1700", "coeurs": 24, "freq": "5.8GHz"},
            {"modèle": "Ryzen 9 7950X", "marque": "AMD", "socket": "AM5", "coeurs": 16, "freq": "5.7GHz"},
            {"modèle": "Intel i9-12900KS", "marque": "Intel", "socket": "LGA1700", "coeurs": 16, "freq": "5.5GHz"},
            {"modèle": "Ryzen Threadripper 3990X", "marque": "AMD", "socket": "sTRX4", "coeurs": 64, "freq": "4.3GHz"},
            {"modèle": "Intel Xeon W-3175X", "marque": "Intel", "socket": "LGA3647", "coeurs": 28, "freq": "4.3GHz"}
        ]
        self.ventilos = [
            # 5 bas de gamme
            {"modèle": "Cooler Master SickleFlow", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Arctic F12", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Thermaltake Pure 12", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Corsair AF120", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Be Quiet! Pure Wings 2", "type": "Air", "diamètre": "120mm"},
            # 5 milieu de gamme
            {"modèle": "Noctua NF-P12", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Corsair LL120 RGB", "type": "Air", "diamètre": "120mm"},
            {"modèle": "NZXT Aer RGB 2", "type": "Air", "diamètre": "140mm"},
            {"modèle": "Phanteks PH-F140MP", "type": "Air", "diamètre": "140mm"},
            {"modèle": "Arctic P14 PWM", "type": "Air", "diamètre": "140mm"},
            # 5 haut de gamme
            {"modèle": "Noctua NF-A12x25", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Be Quiet! Silent Wings 3", "type": "Air", "diamètre": "140mm"},
            {"modèle": "Corsair QL120 RGB", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Lian Li UNI FAN SL120", "type": "Air", "diamètre": "120mm"},
            {"modèle": "Thermaltake Riing Trio", "type": "Air", "diamètre": "120mm"}
        ]
        self.refroidissements = [
            # 5 bas de gamme
            {"modèle": "Cooler Master Hyper 212", "type": "Air", "compatibilité": "AM4/1151"},
            {"modèle": "Arctic Freezer 7 Pro", "type": "Air", "compatibilité": "AM4/LGA1200"},
            {"modèle": "Deepcool GAMMAXX 400", "type": "Air", "compatibilité": "AM4/LGA1200"},
            {"modèle": "Be Quiet! Pure Rock Slim", "type": "Air", "compatibilité": "AM4/LGA1151"},
            {"modèle": "Thermaltake UX100", "type": "Air", "compatibilité": "AM4/LGA1151"},
            # 5 milieu de gamme
            {"modèle": "NZXT Kraken X63", "type": "Watercooling", "compatibilité": "AM4/LGA1700"},
            {"modèle": "Corsair H100i RGB", "type": "Watercooling", "compatibilité": "AM4/LGA1200"},
            {"modèle": "Be Quiet! Pure Loop", "type": "Watercooling", "compatibilité": "AM4/LGA1200"},
            {"modèle": "MSI MAG CoreLiquid 240R", "type": "Watercooling", "compatibilité": "AM4/LGA1700"},
            {"modèle": "Arctic Liquid Freezer II", "type": "Watercooling", "compatibilité": "AM4/LGA1200"},
            # 5 haut de gamme
            {"modèle": "Corsair iCUE H150i Elite", "type": "Watercooling", "compatibilité": "AM4/LGA1700"},
            {"modèle": "NZXT Kraken Z73", "type": "Watercooling", "compatibilité": "AM4/LGA1700"},
            {"modèle": "EK-AIO Elite 360 D-RGB", "type": "Watercooling", "compatibilité": "AM4/LGA1700"},
            {"modèle": "Lian Li Galahad 360", "type": "Watercooling", "compatibilité": "AM4/LGA1700"},
            {"modèle": "Alphacool Eisbaer Aurora", "type": "Watercooling", "compatibilité": "AM4/LGA1700"}
        ]
        from typing import List, Dict, Any
        self.gpus: List[Dict[str, Any]] = [
            # 5 bas de gamme
            {"modèle": "GTX 1050", "marque": "NVIDIA", "VRAM": "2Go", "score": 1000},
            {"modèle": "GTX 1650", "marque": "NVIDIA", "VRAM": "4Go", "score": 2000},
            {"modèle": "RX 550", "marque": "AMD", "VRAM": "2Go", "score": 1200},
            {"modèle": "GT 1030", "marque": "NVIDIA", "VRAM": "2Go", "score": 900},
            {"modèle": "RX 560", "marque": "AMD", "VRAM": "4Go", "score": 1500},
            # 5 milieu de gamme
            {"modèle": "RTX 3060", "marque": "NVIDIA", "VRAM": "12Go", "score": 5000},
            {"modèle": "RX 6600 XT", "marque": "AMD", "VRAM": "8Go", "score": 4800},
            {"modèle": "RTX 3070", "marque": "NVIDIA", "VRAM": "8Go", "score": 7000},
            {"modèle": "RX 6700 XT", "marque": "AMD", "VRAM": "12Go", "score": 6500},
            {"modèle": "RTX 3060 Ti", "marque": "NVIDIA", "VRAM": "8Go", "score": 6000},
            # 5 haut de gamme
            {"modèle": "RTX 4090", "marque": "NVIDIA", "VRAM": "24Go", "score": 12000},
            {"modèle": "RX 7900 XT", "marque": "AMD", "VRAM": "20Go", "score": 11000},
            {"modèle": "RTX 4080", "marque": "NVIDIA", "VRAM": "16Go", "score": 10000},
            {"modèle": "RX 6950 XT", "marque": "AMD", "VRAM": "16Go", "score": 9500},
            {"modèle": "RTX 4070 Ti", "marque": "NVIDIA", "VRAM": "12Go", "score": 9000}
        ]
        from typing import List, Dict, Any
        self.rams: List[Dict[str, Any]] = [
            # 5 bas de gamme
            {"modèle": "4Go DDR3", "type": "DDR3", "taille": "4Go", "freq": "1600MHz", "score": 500},
            {"modèle": "8Go DDR3", "type": "DDR3", "taille": "8Go", "freq": "1600MHz", "score": 800},
            {"modèle": "8Go DDR4", "type": "DDR4", "taille": "8Go", "freq": "2400MHz", "score": 1200},
            {"modèle": "16Go DDR3", "type": "DDR3", "taille": "16Go", "freq": "1600MHz", "score": 1500},
            {"modèle": "8Go DDR4", "type": "DDR4", "taille": "8Go", "freq": "3200MHz", "score": 1300},
            # 5 milieu de gamme
            {"modèle": "16Go DDR4", "type": "DDR4", "taille": "16Go", "freq": "3200MHz", "score": 2000},
            {"modèle": "32Go DDR4", "type": "DDR4", "taille": "32Go", "freq": "3200MHz", "score": 3500},
            {"modèle": "32Go DDR5", "type": "DDR5", "taille": "32Go", "freq": "4800MHz", "score": 4000},
            {"modèle": "64Go DDR4", "type": "DDR4", "taille": "64Go", "freq": "3200MHz", "score": 5000},
            {"modèle": "16Go DDR5", "type": "DDR5", "taille": "16Go", "freq": "5600MHz", "score": 2500},
            # 5 haut de gamme
            {"modèle": "64Go DDR5", "type": "DDR5", "taille": "64Go", "freq": "5600MHz", "score": 6000},
            {"modèle": "128Go DDR4", "type": "DDR4", "taille": "128Go", "freq": "3200MHz", "score": 8000},
            {"modèle": "128Go DDR5", "type": "DDR5", "taille": "128Go", "freq": "5600MHz", "score": 10000},
            {"modèle": "256Go DDR5", "type": "DDR5", "taille": "256Go", "freq": "5600MHz", "score": 15000},
            {"modèle": "256Go DDR4", "type": "DDR4", "taille": "256Go", "freq": "3200MHz", "score": 12000}
        ]
        from typing import List, Dict, Any
        self.storages: List[Dict[str, Any]] = [
            # 5 bas de gamme
            {"modèle": "HDD 250Go", "type": "HDD", "taille": "250Go", "score": 200},
            {"modèle": "HDD 500Go", "type": "HDD", "taille": "500Go", "score": 400},
            {"modèle": "HDD 1To", "type": "HDD", "taille": "1To", "score": 600},
            {"modèle": "SSD 120Go", "type": "SSD", "taille": "120Go", "score": 800},
            {"modèle": "SSD 240Go", "type": "SSD", "taille": "240Go", "score": 1000},
            # 5 milieu de gamme
            {"modèle": "SSD 500Go", "type": "SSD", "taille": "500Go", "score": 1500},
            {"modèle": "SSD 1To", "type": "SSD", "taille": "1To", "score": 2000},
            {"modèle": "NVMe 500Go", "type": "NVMe", "taille": "500Go", "score": 2500},
            {"modèle": "NVMe 1To", "type": "NVMe", "taille": "1To", "score": 3000},
            {"modèle": "NVMe 2To", "type": "NVMe", "taille": "2To", "score": 3500},
            # 5 haut de gamme
            {"modèle": "NVMe 4To", "type": "NVMe", "taille": "4To", "score": 4000},
            {"modèle": "SSD 2To", "type": "SSD", "taille": "2To", "score": 3500},
            {"modèle": "SSD 4To", "type": "SSD", "taille": "4To", "score": 4000},
            {"modèle": "NVMe 8To", "type": "NVMe", "taille": "8To", "score": 8000},
            {"modèle": "SSD 8To", "type": "SSD", "taille": "8To", "score": 8000}
        ]
        self.alims = [
            # 5 bas de gamme
            {"modèle": "250W", "puissance": "250W", "certif": "Bronze"},
            {"modèle": "350W", "puissance": "350W", "certif": "Bronze"},
            {"modèle": "400W", "puissance": "400W", "certif": "Bronze"},
            {"modèle": "450W", "puissance": "450W", "certif": "Bronze"},
            {"modèle": "500W", "puissance": "500W", "certif": "Bronze"},
            # 5 milieu de gamme
            {"modèle": "550W Gold", "puissance": "550W", "certif": "Gold"},
            {"modèle": "650W Gold", "puissance": "650W", "certif": "Gold"},
            {"modèle": "750W Gold", "puissance": "750W", "certif": "Gold"},
            {"modèle": "850W Gold", "puissance": "850W", "certif": "Gold"},
            {"modèle": "650W Platinum", "puissance": "650W", "certif": "Platinum"},
            # 5 haut de gamme
            {"modèle": "1000W Platinum", "puissance": "1000W", "certif": "Platinum"},
            {"modèle": "1200W Platinum", "puissance": "1200W", "certif": "Platinum"},
            {"modèle": "1600W Titanium", "puissance": "1600W", "certif": "Titanium"},
            {"modèle": "2000W Titanium", "puissance": "2000W", "certif": "Titanium"},
            {"modèle": "1800W Platinum", "puissance": "1800W", "certif": "Platinum"}
        ]
        from typing import List, Dict, Any
        self.ecrans: List[Dict[str, Any]] = [
            # 5 bas de gamme
            {"modèle": "Dell S2421HS", "marque": "Dell", "taille": "24\"", "type": "IPS", "hz": 75},
            {"modèle": "AOC 24B1XHS", "marque": "AOC", "taille": "24\"", "type": "IPS", "hz": 60},
            {"modèle": "Philips 243V7QDSB", "marque": "Philips", "taille": "24\"", "type": "IPS", "hz": 75},
            {"modèle": "BenQ GW2480", "marque": "BenQ", "taille": "24\"", "type": "IPS", "hz": 60},
            {"modèle": "HP X24c", "marque": "HP", "taille": "24\"", "type": "VA", "hz": 144},
            # 5 milieu de gamme
            {"modèle": "Samsung Odyssey G5", "marque": "Samsung", "taille": "27\"", "type": "VA", "hz": 144},
            {"modèle": "LG UltraGear 27GL850", "marque": "LG", "taille": "27\"", "type": "IPS", "hz": 144},
            {"modèle": "AOC 24G2U", "marque": "AOC", "taille": "24\"", "type": "IPS", "hz": 144},
            {"modèle": "MSI Optix MAG272CQR", "marque": "MSI", "taille": "27\"", "type": "VA", "hz": 165},
            {"modèle": "Gigabyte G27QC", "marque": "Gigabyte", "taille": "27\"", "type": "VA", "hz": 165},
            # 5 haut de gamme
            {"modèle": "Alienware AW2521HF", "marque": "Alienware", "taille": "25\"", "type": "IPS", "hz": 240},
            {"modèle": "Samsung U32J590", "marque": "Samsung", "taille": "32\"", "type": "VA", "hz": 60},
            {"modèle": "ViewSonic XG2405", "marque": "ViewSonic", "taille": "24\"", "type": "IPS", "hz": 144},
            {"modèle": "Iiyama G-Master GB2760QSU", "marque": "Iiyama", "taille": "27\"", "type": "TN", "hz": 165},
            {"modèle": "Lenovo G27q-20", "marque": "Lenovo", "taille": "27\"", "type": "IPS", "hz": 165}
        ]
        # ... idem pour GPU, RAM, Stockage, Alim ...

    def build_sidebar(self):
        self.sidebar_expanded = True

        def toggle_sidebar():
            if self.sidebar_expanded:
                self.sidebar.pack_forget()
                self.sidebar_expanded = False
                self.sidebar_btn = tk.Button(self, text="⏩", bg="#222", fg="#FFD700", font=("Arial", 12, "bold"),
                                             command=toggle_sidebar, relief="flat", bd=0, activebackground="#333")
                self.sidebar_btn.place(x=0, y=0)
            else:
                self.sidebar.pack(side="left", fill="y")
                self.sidebar_expanded = True
                if hasattr(self, "sidebar_btn") and self.sidebar_btn is not None:
                    self.sidebar_btn.destroy()

        toggle_btn = tk.Button(self.sidebar, text="⏪", bg="#222", fg="#FFD700", font=("Arial", 12, "bold"),
                              command=toggle_sidebar, relief="flat", bd=0, activebackground="#333")
        toggle_btn.pack(pady=5, anchor="ne")

        from typing import List, Tuple, Callable, Any
        sections: List[Tuple[str, List[Tuple[str, Callable[[], Any]]]]] = [
            ("Général", [
                ("🏠 Dashboard", self.load_dashboard),
                ("📊 Stats", self.load_stats),
                ("📜 Changelog", self.load_changelog),
                ("❓ Aide", self.load_help),
                ("🔄 Reboot", self.trigger_reboot),
            ]),
            ("Gestion", [
                ("🔧 Config", self.load_config),
                ("🛠️ Admin", self.load_admin),
                ("🔄 Modules", self.load_modules),
                ("💬 Logs", self.load_logs),
                ("⚙️ Paramètres", self.load_settings),
                ("🌐 Serveurs Discord", self.load_discord_servers),
            ]),
            ("Jeux & Casino", [
                ("🎮 Jeux", self.load_games),
                ("🃏 Poker", self.load_poker),
                ("🎲 Reel Pocket", self.load_reel_pocket),
                ("🏹 Donjon RPG", self.load_dungeon),
                ("📈 Casino Stats", self.load_casino_stats),
            ]),
            ("Hubs & Whitelist", [
                ("🛠️ Config Hubs", self.load_config_hub),
                ("⚙️ Gérer ADC Whitelist", self.manage_adc_whitelist),
                ("🧠 Bugs", self.load_bugs),
            ]),
            ("Social", [
                ("💬 Chat Global", self.load_chat),
                ("🛒 Boutique", self.show_shop_gui),
                ("🌐 Liste des serveurs", self.load_discord_servers),
            ])
        ]
        for section, btns in sections:
            tk.Label(self.sidebar, text=section, fg="#00f2ff", bg="#2c2c2c", font=("Arial", 10, "bold")).pack(pady=(15, 3))
            for label, command in btns:
                neon_color = "#00eaff" if "Jeux" in section or "Casino" in section else "#ff00cc"
                tk.Button(
                    self.sidebar,
                    text=label,
                    font=("Arial", 10, "bold"),
                    fg="white",
                    bg=neon_color,
                    activebackground="#3a3a3a",
                    relief="groove",
                    bd=2,
                    highlightbackground=neon_color,
                    highlightthickness=2,
                    command=command
                ).pack(fill="x", pady=4)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def load_dashboard(self):
        self.clear_content()
        self.active_tab = "dashboard"
        neon_bar = tk.Frame(self.content, bg="#00eaff", height=8)
        neon_bar.pack(fill="x", pady=(0, 10))
        tk.Label(self.content, text="🧠 Arsenal • Creator Dashboard", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#00FF88").pack(pady=20)
        stats_frame = tk.Frame(self.content, bg="#1e1e1e")
        stats_frame.pack(pady=20, padx=30, fill="x")
        stats = {
            "🧑‍💻 Utilisateur": os.getenv("USERNAME", "Inconnu"),
            "🕒 Heure": datetime.now().strftime("%H:%M:%S"),
            "🔋 RAM": f"{round(sys.getsizeof(stats_frame)/1024/1024,2)} Mo utilisée",
            "🌐 Serveurs": len(getattr(self.bot, "guilds", [])),
            "💬 Commandes": len(getattr(self.bot.tree, "get_commands", lambda: [])()),
            "🎲 Jeux disponibles": 5,
            "🛠️ Modules actifs": 8,
            "⚙️ Version": "v3.5"
        }
        for i, (label, value) in enumerate(stats.items()):
            box = tk.Frame(stats_frame, bg="#2c2c2c", padx=20, pady=15)
            box.grid(row=0, column=i, padx=15)
            tk.Label(box, text=label, font=("Arial", 12, "bold"), bg="#2c2c2c", fg="#FFDD00").pack()
            tk.Label(box, text=str(value), font=("Consolas", 14), bg="#2c2c2c", fg="#00FF88").pack()
        tk.Label(self.content, text="Bienvenue sur Arsenal Studio ! Utilise la sidebar pour explorer toutes les fonctionnalités.", bg="#1e1e1e", fg="gray", font=("Arial", 12)).pack(pady=15)
    
    def load_stats(self):
        self.clear_content()
        self.active_tab = "stats"
        tk.Label(self.content, text="📊 Statistiques Globales • Arsenal Studio",
                 font=("Helvetica", 18, "bold"), bg="#1e1e1e", fg="#00FF88").pack(pady=15)
        cmd_stats = getattr(self.bot, "command_usage", {})
        total_cmds = sum(cmd_stats.values())
        unique_cmds = len(cmd_stats)
        top_cmds = sorted(cmd_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        tk.Label(self.content, text=f"🧮 Commandes utilisées : {total_cmds}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"📌 Commandes uniques : {unique_cmds}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"🌐 Serveurs connectés : {len(getattr(self.bot, 'guilds', []))}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"🛠️ Modules actifs : 8", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"🎲 Jeux disponibles : 5", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=5)
        # Top commandes
        top_frame = tk.Frame(self.content, bg="#1e1e1e")
        top_frame.pack(pady=10)
        tk.Label(top_frame, text="🏆 Commandes les plus utilisées :", bg="#1e1e1e", fg="#FFD700", font=("Arial", 13, "bold")).pack(anchor="w", padx=10)
        for cmd_name, usage_count in top_cmds:
            tk.Label(top_frame, text=f"• {cmd_name} → {usage_count} fois", bg="#1e1e1e", fg="white", font=("Arial", 11)).pack(anchor="w", padx=20)
        tk.Button(self.content, text="🔄 Recharger les statistiques", bg="#2e8b57", fg="white", command=self.load_stats).pack(pady=15)
        # 🔍 Commande spécifique à analyser
        tk.Label(self.content, text="🔎 Analyse individuelle :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)
        entry = tk.Entry(self.content, bg="gray", fg="white", width=30)
        entry.pack(pady=5)

        result_lbl = tk.Label(self.content, text="", bg="#1e1e1e", fg="cyan", font=("Consolas", 11))
        result_lbl.pack(pady=5)

        def check_command_usage():
            cmd = entry.get()
            count = cmd_stats.get(cmd, 0)
            total = total_cmds or 1
            pct = round((count / total) * 100, 2)
            result_lbl.config(text=f"/{cmd} ➜ {count} exécutions ({pct}%)")

        tk.Button(self.content, text="📊 Voir", command=check_command_usage, bg="#333", fg="white").pack(pady=5)

    # (Remove this entire duplicate method block. Keep only one definition of load_config in the class.)

    # (REMOVE THIS DUPLICATE DEFINITION)

    # (Removed duplicate definition of manage_adc_whitelist)

    def remove_adc_id(self, key: str) -> None:
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(".env", "w", encoding="utf-8") as f:
            for line in lines:
                if not line.startswith(key + "="):
                    f.write(line)
        messagebox.showinfo(str("❌ Supprimé"), str(f"{key} retiré de la whitelist."))
        self.manage_adc_whitelist()

    def load_games(self):
        self.clear_content()
        eco = load_economie()
        uid = str(self.bot.user.id)

        tk.Label(self.content, text="🎮 Zone de Jeux • Arsenal Casino", font=("Helvetica", 18, "bold"),
                 bg="#FFD700", fg="black").pack(pady=10)

        tk.Label(self.content, text="💸 Montant à miser (en AC) :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack()
        tk.Entry(self.content, textvariable=self.bet_var, bg="gray", fg="white", width=12).pack(pady=5)

        from typing import List, Tuple, Callable, Any
        btns: List[Tuple[str, Callable[[dict[str, Any], str], None]]] = [
            ("🃏 Blackjack", self.choisir_table_blackjack),
            ("🎲 Spin Roulette", self.lancer_spin_gui),
            ("🎯 Devine le Nombre", self.lancer_guess_gui)
        ]
        for label, action in btns:
            tk.Button(self.content, text=label, bg="#333", fg="white",
                      font=("Arial", 12), command=lambda a=action: a(eco, uid)).pack(pady=6)

    def choisir_table_blackjack(self, eco: dict[str, Any], uid: str) -> None:
        self.clear_content()
        self.active_tab = "blackjack_tables"
        from typing import List, Dict, Any
        tables: List[Dict[str, Any]] = [
            {"nom": "Table 1", "min": 100, "max": 1000},
            {"nom": "Table 2", "marque": "MSI", "min": 1000, "max": 5000},
            {"nom": "Table 3", "marque": "MSI", "min": 5000, "max": 20000},
            {"nom": "Table 4", "marque": "MSI", "min": 20000, "max": 100000},
        ]
        tk.Label(self.content, text="🃏 Choisis ta table de Blackjack", font=("Helvetica", 20, "bold"),
                 bg="#145a32", fg="#FFD700").pack(pady=30)
        frame = tk.Frame(self.content, bg="#145a32")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        solde = get_balance(uid, eco)
        for t in tables:
            txt = f"{t['nom']} — Mise : {t['min']} à {t['max']} AC"
            def try_lancer(t: dict[str, Any] = t):
                if solde < t["min"]:
                    messagebox.showwarning("Solde insuffisant", f"Tu n'as pas assez d'ArsenalCoins pour jouer à cette table.\nSolde actuel : {solde} AC\nMise minimale : {t['min']} AC")  # type: ignore
                    self.load_games()
                else:
                    self.lancer_blackjack_gui(eco, uid, t)
            tk.Button(self.content, text=txt, font=("Arial", 14, "bold"), bg="#229954", fg="white",
                      width=30, pady=10, command=try_lancer).pack(pady=15)

    def lancer_blackjack_gui(self, eco: dict[str, Any], uid: str, table: dict[str, Any]) -> None:
        self.clear_content()
        self.active_tab = "blackjack"
        self.blackjack_table = table
        self.deck = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] * 4
        random.shuffle(self.deck)
        self.player_hands = [[self.deck.pop(), self.deck.pop()]]
        self.active_hand = 0
        self.bot_hand = [self.deck.pop(), self.deck.pop()]
        self.bet_amounts = [table["min"]]
        self.bj_game_over = False
        self.bj_doubled = [False]
        self.bj_split_count = 0
        self.show_blackjack_state(eco, uid)

    def calc_blackjack_total(self, hand):
        total, aces = 0, 0
        for c in hand:
            if c in ["J", "Q", "K"]:
                total += 10
            elif c == "A":
                aces += 1
                total += 11
            else:
                total += int(c)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def show_blackjack_state(self, eco: dict[str, Any], uid: str) -> None:
        for w in self.content.winfo_children():
            w.destroy()
        solde = get_balance(uid, eco)
        heure = datetime.now().strftime("%H:%M:%S")
        # Affichage unique du solde et de l'heure en haut à droite
        solde_lbl = tk.Label(self.content, text=f"💰 {solde} AC   🕒 {heure}", font=("Arial", 11, "bold"),
                             bg="#1e1e1e", fg="#FFD700", anchor="e")
        solde_lbl.pack(anchor="ne", padx=20, pady=5)

        center_frame = tk.Frame(self.content, bg="#1e1e1e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        def format_hand(hand, reveal_all=True):
            suits = ["♠", "♥", "♦", "♣"]
            emoji_map = {
                "A": "A", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
                "7": "7", "8": "8", "9": "9", "10": "10", "J": "J", "Q": "Q", "K": "K"
            }
            if reveal_all:
                return "  ".join(f"{emoji_map.get(c, c)}{random.choice(suits)}" for c in hand)
            else:
                return f"{emoji_map.get(hand[0], hand[0])}{random.choice(suits)} 🂠"

        p_total = self.calc_blackjack_total(self.player_hands[self.active_hand])
        b_total = self.calc_blackjack_total(self.bot_hand)

        # Croupier (en haut)
        dealer_frame = tk.Frame(center_frame, bg="#1e1e1e")
        dealer_frame.pack(pady=10)
        tk.Label(dealer_frame, text="🤖 Croupier", font=("Arial", 13, "bold"), bg="#1e1e1e", fg="#FF7788").pack()
        if not self.bj_game_over:
            tk.Label(dealer_frame, text=format_hand(self.bot_hand, reveal_all=False), font=("Arial", 30),
                     bg="#1e1e1e", fg="white").pack()
            tk.Label(dealer_frame, text="Total : ?", font=("Arial", 12), bg="#1e1e1e", fg="red").pack()
        else:
            tk.Label(dealer_frame, text=format_hand(self.bot_hand), font=("Arial", 30), bg="#1e1e1e", fg="white").pack()
            tk.Label(dealer_frame, text=f"Total : {b_total}", font=("Arial", 12), bg="#1e1e1e", fg="red").pack()

        # Joueur (en bas)
        player_frame = tk.Frame(center_frame, bg="#1e1e1e")
        player_frame.pack(pady=10)
        tk.Label(player_frame, text="🧑‍💼 Toi", font=("Arial", 13, "bold"), bg="#1e1e1e", fg="#00FF88").pack()
        tk.Label(player_frame, text=format_hand(self.player_hands[self.active_hand]), font=("Arial", 30),
                 bg="#1e1e1e", fg="white").pack()
        tk.Label(player_frame, text=f"Total : {p_total}", font=("Arial", 12), bg="#1e1e1e", fg="lime").pack()

        # Gestion de la fin de partie
        if self.bj_game_over:
            return

        # Boutons d'action
        btn_frame = tk.Frame(center_frame, bg="#1e1e1e")
        btn_frame.pack(pady=15)

        # Hit et Stand toujours disponibles
        tk.Button(btn_frame, text="➕ Hit", font=("Arial", 12, "bold"), bg="#2e8b57", fg="white",
                  width=10, command=lambda: self.hit_blackjack(eco, uid)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="✅ Stand", font=("Arial", 12, "bold"), bg="#3399FF", fg="white",
                  width=10, command=lambda: self.stand_blackjack(eco, uid)).pack(side="left", padx=10)

        # Double disponible si main à 2 cartes et pas déjà doublée
        if len(self.player_hands[self.active_hand]) == 2 and not self.bj_doubled[self.active_hand]:
            tk.Button(btn_frame, text="✖️ Double", font=("Arial", 12, "bold"), bg="#FFD700", fg="black",
                      width=10, command=lambda: self.double_blackjack(eco, uid)).pack(side="left", padx=10)

        # Split disponible si main à 2 cartes identiques et max 4 mains
        hand = self.player_hands[self.active_hand]
        if len(hand) == 2 and hand[0] == hand[1] and len(self.player_hands) < 4:
            tk.Button(btn_frame, text="🔀 Split", font=("Arial", 12, "bold"), bg="#00FF88", fg="black",
                      width=10, command=lambda: self.split_blackjack(eco, uid)).pack(side="left", padx=10)

        # Vérifie si le joueur a fait un blackjack ou bust
        if p_total == 21:
            self.end_blackjack(eco, uid, "blackjack")
            return
        if p_total > 21:
            self.end_blackjack(eco, uid, "bust")
            return

        eco = load_economie()
        solde = get_balance(uid, eco)
        heure = datetime.now().strftime("%H:%M:%S")
        solde_lbl = tk.Label(self.content, text=f"💰 {solde} AC   🕒 {heure}", font=("Arial", 11, "bold"),
                             bg="#1e1e1e", fg="#FFD700", anchor="e")
        solde_lbl.pack(anchor="ne", padx=20, pady=5)

    def hit_blackjack(self, eco, uid):
        if self.bj_game_over:
            return
        self.player_hands[self.active_hand].append(self.deck.pop())
        self.show_blackjack_state(eco, uid)

    def stand_blackjack(self, eco, uid):
        if self.bj_game_over:
            return
        def calc_total(h): return self.calc_blackjack_total(h)
        while calc_total(self.bot_hand) < 17:
            self.bot_hand.append(self.deck.pop())
        self.end_blackjack(eco, uid)  # <-- retire "stand"

    def double_blackjack(self, eco, uid):
        if self.bj_game_over or len(self.player_hands) > 1:
            return
        self.bet_amounts[self.active_hand] *= 2
        self.hit_blackjack(eco, uid)
        self.stand_blackjack(eco, uid)

    def split_blackjack(self, eco, uid):
        if self.bj_game_over or len(self.player_hands) > 2:
            return
        new_hand = [self.player_hands[self.active_hand].pop(1)]
        self.player_hands.append(new_hand)
        self.bet_amounts.append(self.bet_amounts[self.active_hand])
        self.show_blackjack_state(eco, uid)

    def end_blackjack(self, eco, uid):
        self.bj_game_over = True
        p_totals = [self.calc_blackjack_total(hand) for hand in self.player_hands]
        b_total = self.calc_blackjack_total(self.bot_hand)
        results = []
        gains = []

        for i, p_total in enumerate(p_totals):
            if p_total > 21:
                gains.append(-self.bet_amounts[i])
                results.append("💥 Bust")
            elif b_total > 21 or p_total > b_total:
                gains.append(self.bet_amounts[i])
                results.append("🎉 Gagné")
            elif p_total == b_total:
                gains.append(0)
                results.append("🤝 Égalité")
            else:
                gains.append(-self.bet_amounts[i])
                results.append("❌ Perdu")

        # Affichage des résultats
        for i, result in enumerate(results):
            txt = f"Main {i+1} : {result} {'+' + str(gains[i]) + ' AC' if gains[i] > 0 else ''}"
            tk.Label(self.content, text=txt, font=("Helvetica", 16, "bold"), fg="#FFD700", bg="#1e1e1e").pack(pady=10)

        # Mise à jour des soldes
        for i, gain in enumerate(gains):
            update_balance(uid, gain, eco, f"Blackjack {'Main ' + str(i+1)}")

        tk.Button(self.content, text="🔄 Rejouer", bg="#333", fg="white",
                  font=("Arial", 12, "bold"), command=lambda: self.choisir_table_blackjack(eco, uid)).pack(pady=5)

    def lancer_spin_gui(self, eco: dict[str, Any], uid: str) -> None:
        self.clear_content()
        bet = int(self.bet_var.get())
        result = random.choice(["💰 Gagné", "💀 Perdu", "🎲 Jackpot"])
        gain = -bet if result == "💀 Perdu" else bet * 2 if result == "🎲 Jackpot" else -bet + int(bet * 1.3)

        update_balance(uid, gain, eco, f"Spin ➜ {result}")
        msg = f"🎡 Résultat : {result}\n{'+' if gain > 0 else ''}{gain} AC"
        tk.Label(self.content, text=msg, font=("Arial", 14), bg="#1e1e1e", fg="cyan").pack(pady=10)

    def lancer_guess_gui(self, eco: dict[str, Any], uid: str) -> None:
        self.clear_content()
        bet = int(self.bet_var.get())
        secret = random.randint(1, 10)

        tk.Label(self.content, text="🎯 Choisis un nombre (1–10)", font=("Arial", 12), bg="#1e1e1e", fg="white").pack(pady=5)
        entry = tk.Entry(self.content, bg="gray", fg="white")
        entry.pack(pady=5)

        def validate_guess():
            guess = int(entry.get())
            if guess == secret:
                update_balance(uid, bet * 2, eco, f"Guess ✅ Gagné : {guess}")
                msg = f"🔥 Bravo ! C'était {secret} ➜ +{bet * 2} AC"
            else:
                update_balance(uid, -bet, eco, f"Guess ❌ Raté : {guess}")
                msg = f"❌ Mauvais choix. C'était {secret} ➜ -{bet} AC"
            tk.Label(self.content, text=msg, bg="#1e1e1e", fg="orange", font=("Arial", 12)).pack(pady=8)

        tk.Button(self.content, text="🎯 Valider", bg="blue", fg="white", command=validate_guess).pack(pady=5)

    def load_config_hub(self):
        self.clear_content()
        self.active_tab = "config_hub"

        tk.Label(self.content, text="🛠️ Configuration des Hubs Vocaux", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)

        try:
            with open("data/hub_config.json", "r", encoding="utf-8") as f:
                hub_data = json.load(f)
        except:
            tk.Label(self.content, text="❌ Impossible de charger hub_config.json", fg="red", bg="#1e1e1e").pack()
            return

        for hub_id, hub in hub_data.items():
            frame = tk.Frame(self.content, bg="#2c2c2c", pady=8, padx=15)
            frame.pack(fill="x", padx=20, pady=6)

            main_name = self.bot.get_channel(hub["main_channel_id"]).name if self.bot.get_channel(hub["main_channel_id"]) else "❓"
            tk.Label(frame, text=f"📡 Hub : {main_name}", font=("Arial", 14, "bold"),
                     bg="#2c2c2c", fg="white").pack(anchor="w")

            tk.Label(frame, text=f"👑 Propriétaire : <@{hub['owner_id']}>", bg="#2c2c2c", fg="gray").pack(anchor="w")
            tk.Label(frame, text=f"🗂 Catégorie : {hub['category_id']}", bg="#2c2c2c", fg="gray").pack(anchor="w")

            mods = hub.get("moderators_ids", {})
            tk.Label(frame, text=f"🧑‍💼 Modérateurs ({len(mods)}):", font=("Arial", 11), bg="#2c2c2c", fg="#00FF88").pack(anchor="w", pady=5)

            for uid, perms in mods.items():
                tk.Label(frame, text=f"• <@{uid}> → {', '.join(perms)}", bg="#2c2c2c", fg="gray").pack(anchor="w")

            tk.Button(frame, text="🔧 Modifier les permissions", bg="blue", fg="white",
                      command=lambda uid=hub['owner_id'], hid=hub_id: self.modify_mod_permissions(uid, hid) if hasattr(self, "modify_mod_permissions") else None).pack(side="left", padx=5)
            tk.Button(frame, text="🗑️ Supprimer ce Hub", bg="red", fg="white",
                      command=lambda hid=hub_id: self.delete_hub(hid)).pack(side="left", padx=5)

    def delete_hub(self, hub_id):
        with open("data/hub_config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if hub_id in data:
            del data[hub_id]
            with open("data/hub_config.json", "w", encoding="utf-8") as f2:
                json.dump(data, f2, indent=4)
            messagebox.showinfo("Hub supprimé", f"Le hub {hub_id} a été supprimé.")
            self.load_config_hub()

    def load_casino_stats(self):
        self.clear_content()
        eco = load_economie()
        uid = str(self.bot.user.id)

        tk.Label(self.content, text="📈 Stats Casino • Arsenal Studio", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#33CCFF").pack(pady=10)

        # 💰 Solde actuel
        solde = get_balance(uid, eco)
        tk.Label(self.content, text=f"💰 Ton solde : {solde} ArsenalCoins", bg="#1e1e1e", fg="lime",
                 font=("Arial", 14)).pack(pady=8)

        # 🧠 Historique personnel
        tk.Label(self.content, text="🗂 Historique récent :", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=4)
        history = get_history(uid, eco)
        for h in reversed(history):
            txt = f"{h['date']} ➜ {h['jeu']} ➜ {'+' if h['gain']>0 else ''}{h['gain']} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="gray").pack(anchor="w")

        # 👑 Top joueurs
        tk.Label(self.content, text="👑 Top 5 joueurs : ", bg="#1e1e1e", fg="#FFD700",
                 font=("Arial", 12)).pack(pady=10)
        leaderboard = get_leaderboard(eco)

        for i, (user_id, balance) in enumerate(leaderboard, start=1):
            name = "Toi" if str(user_id) == uid else f"User#{str(user_id)[-5:]}"
            txt = f"{i}. {name} ➜ {balance} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="orange").pack(anchor="w")

        # 🧮 Résumé en chiffres
        summary_frame = tk.Frame(self.content, bg="#2c2c2c", pady=10)
        summary_frame.pack(fill="x", padx=30)

        cmd_stats = getattr(self.bot, "command_usage", {})
        total_cmds = sum(cmd_stats.values())
        unique_cmds = len(cmd_stats)
        top_cmds = sorted(cmd_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        info = {
            "📘 Commandes enregistrées": len(self.bot.tree.get_commands()),
            "🔢 Total d'exécutions": total_cmds,
            "🧠 Commandes uniques utilisées": unique_cmds,
            "🔝 Top commandes listées": len(top_cmds)
        }

        for k, v in info.items():
            box = tk.Frame(summary_frame, bg="#2c2c2c", padx=10, pady=8)
            box.pack(side="left", padx=15)
            tk.Label(box, text=k, font=("Arial", 10, "bold"), bg="#2c2c2c", fg="#FFD700").pack()
            tk.Label(box, text=str(v), font=("Consolas", 12), bg="#2c2c2c", fg="#00FF88").pack()

        # 🔝 Top 10 commandes les plus utilisées avec barres
        bar_frame = tk.Frame(self.content, bg="#1e1e1e")
        bar_frame.pack(pady=10)

        tk.Label(bar_frame, text="🏆 Top 10 Commandes", font=("Arial", 14), bg="#1e1e1e", fg="white").pack(pady=5)

        max_usage = top_cmds[0][1] if top_cmds else 1

        for cmd, count in top_cmds:
            bar_container = tk.Frame(bar_frame, bg="#1e1e1e")
            bar_container.pack(fill="x", padx=25, pady=4)

            tk.Label(bar_container, text=f"• /{cmd}", font=("Arial", 10), bg="#1e1e1e", fg="#FFDD00", width=20, anchor="w").pack(side="left")

            bar_width = int((count / max_usage) * 200)
            bar = tk.Frame(bar_container, bg="#00FF88", width=bar_width, height=14)
            bar.pack(side="left")

            tk.Label(bar_container, text=f"{count}×", font=("Consolas", 10), bg="#1e1e1e", fg="gray", width=6).pack(side="left")

        # 🔍 Commande spécifique à analyser
        tk.Label(self.content, text="🔎 Analyse individuelle :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)
        entry = tk.Entry(self.content, bg="gray", fg="white", width=30)
        entry.pack()

        result_lbl = tk.Label(self.content, text="", bg="#1e1e1e", fg="cyan", font=("Consolas", 11))
        result_lbl.pack(pady=5)

        def check_command_usage():
            cmd = entry.get()
            count = cmd_stats.get(cmd, 0)
            total = total_cmds or 1
            pct = round((count / total) * 100, 2)
            result_lbl.config(text=f"/{cmd} ➜ {count} exécutions ({pct}%)")

        tk.Button(self.content, text="📊 Voir", command=check_command_usage, bg="#333", fg="white").pack(pady=5)

    def load_config(self):
        self.clear_content()
        self.active_tab = "config"

        tk.Label(self.content, text="🔧 Panneau Configuration", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)

        config_path = "data/config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except:
            config = {}

        entries = {}
        tooltips = {
            "bot_name": "Nom affiché du bot sur Discord",
            "prefix": "Préfixe pour les commandes textuelles",
            "creator_id": "ID Discord du créateur principal",
            "lang": "Langue principale du bot",
            "maintenance": "Activer/désactiver le mode maintenance",
            "main_color": "Couleur principale du thème (hex)",
            "show_balance": "Afficher le solde dans le dashboard",
            "log_level": "Niveau de logs (info, debug, warning, error)"
        }
        params = [
            ("Nom du bot", "bot_name"),
            ("Préfixe des commandes", "prefix"),
            ("ID du créateur", "creator_id"),
            ("Langue", "lang"),
            ("Mode maintenance (on/off)", "maintenance"),
            ("Couleur principale", "main_color"),
            ("Afficher le solde", "show_balance"),
            ("Niveau de logs", "log_level"),
        ]
        for label, key in params:
            frame = tk.Frame(self.content, bg="#1e1e1e")
            frame.pack(pady=5, padx=20, anchor="w")
            tk.Label(frame, text=label + " :", bg="#1e1e1e", fg="white", width=22, anchor="w").pack(side="left")
            val = str(config.get(key, ""))
            entry = tk.Entry(frame, width=30)
            entry.insert(0, val)
            entry.pack(side="left")
            entries[key] = entry
            # Tooltip
            tip = tooltips.get(key, "")
            if tip:
                tk.Label(frame, text=f"ⓘ {tip}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 8)).pack(side="left")

        def save_config():
            for k, entry in entries.items():
                config[k] = entry.get()
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("✅ Sauvegardé", "Configuration enregistrée.")

        tk.Button(self.content, text="💾 Sauvegarder", bg="#2e8b57", fg="white", command=save_config,
                  font=("Arial", 12, "bold"), relief="groove", bd=2, activebackground="#00FF88").pack(pady=20)

    def load_bugs(self):
        self.clear_content()
        self.active_tab = "bugs"

        tk.Label(
            self.content,
            text="🧠 Panneau Bugs & Feedbacks",
            font=("Helvetica", 18, "bold"),
            bg="#1e1e1e",
            fg="#FF7788"
        ).pack(pady=15)

        tk.Label(
            self.content,
            text="Tu peux noter ici les retours, bugs rencontrés ou idées pour la version suivante.",
            bg="#1e1e1e",
            fg="gray",
            font=("Arial", 11),
            wraplength=700,
            justify="left"
        ).pack(pady=10)

        # Zone de texte feedback
        feedback_box = tk.Text(self.content, height=10, width=80, bg="#2c2c2c", fg="white", insertbackground="white")
        feedback_box.pack(pady=10)

        def enregistrer_feedback():
            feedback = feedback_box.get("1.0", "end").strip()
            if feedback:
                with open("logs/bugs_feedback.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {feedback}\n\n")
                messagebox.showinfo("✅ Enregistré", "Ton retour a bien été sauvegardé.")
                feedback_box.delete("1.0", "end")

        tk.Button(
            self.content,
            text="📤 Envoyer le feedback",
            bg="#3399FF",
            fg="white",
            command=enregistrer_feedback
        ).pack(pady=10)

    def manage_adc_whitelist(self):
        self.clear_content()
        self.active_tab = "adc_whitelist"

        tk.Label(
            self.content,
            text="⚙️ Gestion ADC Whitelist",
            font=("Helvetica", 18, "bold"),
            bg="#1e1e1e",
            fg="#FFD700"
        ).pack(pady=15)

        whitelist_frame = tk.Frame(self.content, bg="#2c2c2c")
        whitelist_frame.pack(pady=10)

        for key, val in os.environ.items():
            if key.startswith("XeroX") or key.startswith("ADC_"):
                row = tk.Frame(whitelist_frame, bg="#2c2c2c")
                row.pack(fill="x", pady=5, padx=15)

                tk.Label(
                    row,
                    text=f"{key} : {val}",
                    bg="#2c2c2c",
                    fg="white"
                ).pack(side="left")

                tk.Button(
                    row,
                    text="❌ Supprimer",
                    bg="red",
                    fg="white",
                    command=lambda k=key: self.remove_adc_id(k)
                ).pack(side="right")

        # 📥 Ajout manuel
        entry_frame = tk.Frame(self.content, bg="#1e1e1e")
        entry_frame.pack(pady=15)

        tk.Label(entry_frame, text="Nom variable (.env)", bg="#1e1e1e", fg="white").grid(row=0, column=0)
        var_entry = tk.Entry(entry_frame)
        var_entry.grid(row=0, column=1)

        tk.Label(entry_frame, text="ID Discord", bg="#1e1e1e", fg="white").grid(row=1, column=0)
        id_entry = tk.Entry(entry_frame)
        id_entry.grid(row=1, column=1)

        def add_whitelist_entry():
            name = var_entry.get().strip()
            did = id_entry.get().strip()
            if name and did:
                with open(".env", "a", encoding="utf-8") as f:
                    f.write(f"\n{name}={did}")
                messagebox.showinfo("✅ Ajouté", f"{name} = {did} ajouté à la whitelist.")
                self.manage_adc_whitelist()

        tk.Button(
            entry_frame,
            text="➕ Ajouter",
            bg="green",
            fg="white",
            command=add_whitelist_entry
        ).grid(row=2, columnspan=2, pady=10)

    def remove_adc_id(self, key):
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(".env", "w", encoding="utf-8") as f:
            for line in lines:
                if not line.startswith(key + "="):
                    f.write(line)
        messagebox.showinfo("❌ Supprimé", f"{key} retiré de la whitelist.")
        self.manage_adc_whitelist()

    def load_games(self):
        self.clear_content()
        eco = load_economie()
        uid = str(self.bot.user.id)

        tk.Label(self.content, text="🎮 Zone de Jeux • Arsenal Casino", font=("Helvetica", 18, "bold"),
                 bg="#FFD700", fg="black").pack(pady=10)

        tk.Label(self.content, text="💸 Montant à miser (en AC) :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack()
        tk.Entry(self.content, textvariable=self.bet_var, bg="gray", fg="white", width=12).pack(pady=5)

        btns = [
            ("🃏 Blackjack", self.choisir_table_blackjack),
            ("🎲 Spin Roulette", self.lancer_spin_gui),
            ("🎯 Devine le Nombre", self.lancer_guess_gui)
        ]
        for label, action in btns:
            tk.Button(self.content, text=label, bg="#333", fg="white",
                      font=("Arial", 12), command=lambda a=action: a(eco, uid)).pack(pady=6)

        tk.Button(self.content, text="🎲 Spin Roulette", bg="#333", fg="#FFD700",
                  font=("Arial", 12, "bold"), relief="raised", bd=2, command=...).pack(pady=8)

    def choisir_table_blackjack(self, eco: dict[str, Any], uid: str) -> None:
        self.clear_content()
        self.active_tab = "blackjack_tables"
        tables = [
            {"nom": "Table 1", "min": 100, "max": 1000},
            {"nom": "Table 2", "marque": "MSI", "min": 1000, "max": 5000},
            {"nom": "Table 3", "marque": "MSI", "min": 5000, "max": 20000},
            {"nom": "Table 4", "marque": "MSI", "min": 20000, "max": 100000},
        ]
        tk.Label(self.content, text="🃏 Choisis ta table de Blackjack", font=("Helvetica", 20, "bold"),
                 bg="#145a32", fg="#FFD700").pack(pady=30)
        frame = tk.Frame(self.content, bg="#145a32")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        solde = get_balance(uid, eco)
        for t in tables:
            txt = f"{t['nom']} — Mise : {t['min']} à {t['max']} AC"
            def try_lancer(t=t):
                if solde < t["min"]:
                    messagebox.showwarning("Solde insuffisant", f"Tu n'as pas assez d'ArsenalCoins pour jouer à cette table.\nSolde actuel : {solde} AC\nMise minimale : {t['min']} AC")
                    self.load_games()
                else:
                    self.lancer_blackjack_gui(eco, uid, t)
            tk.Button(self.content, text=txt, font=("Arial", 14, "bold"), bg="#229954", fg="white",
                      width=30, pady=10, command=try_lancer).pack(pady=15)

    def lancer_blackjack_gui(self, eco: dict[str, Any], uid: str, table: dict[str, Any]) -> None:
        self.clear_content()
        self.active_tab = "blackjack"
        self.blackjack_table = table
        self.deck = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"] * 4
        random.shuffle(self.deck)
        self.player_hands = [[self.deck.pop(), self.deck.pop()]]
        self.active_hand = 0
        self.bot_hand = [self.deck.pop(), self.deck.pop()]
        self.bet_amounts = [table["min"]]
        self.bj_game_over = False
        self.bj_doubled = [False]
        self.bj_split_count = 0
        self.show_blackjack_state(eco, uid)

    def calc_blackjack_total(self, hand):
        total, aces = 0, 0
        for c in hand:
            if c in ["J", "Q", "K"]:
                total += 10
            elif c == "A":
                aces += 1
                total += 11
            else:
                total += int(c)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def show_blackjack_state(self, eco: dict[str, Any], uid: str) -> None:
        for w in self.content.winfo_children():
            w.destroy()
        solde = get_balance(uid, eco)
        heure = datetime.now().strftime("%H:%M:%S")
        # Affichage unique du solde et de l'heure en haut à droite
        solde_lbl = tk.Label(self.content, text=f"💰 {solde} AC   🕒 {heure}", font=("Arial", 11, "bold"),
                             bg="#1e1e1e", fg="#FFD700", anchor="e")
        solde_lbl.pack(anchor="ne", padx=20, pady=5)

        center_frame = tk.Frame(self.content, bg="#1e1e1e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        def format_hand(hand, reveal_all=True):
            suits = ["♠", "♥", "♦", "♣"]
            emoji_map = {
                "A": "A", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
                "7": "7", "8": "8", "9": "9", "10": "10", "J": "J", "Q": "Q", "K": "K"
            }
            if reveal_all:
                return "  ".join(f"{emoji_map.get(c, c)}{random.choice(suits)}" for c in hand)
            else:
                return f"{emoji_map.get(hand[0], hand[0])}{random.choice(suits)} 🂠"

        p_total = self.calc_blackjack_total(self.player_hands[self.active_hand])
        b_total = self.calc_blackjack_total(self.bot_hand)

        # Croupier (en haut)
        dealer_frame = tk.Frame(center_frame, bg="#1e1e1e")
        dealer_frame.pack(pady=10)
        tk.Label(dealer_frame, text="🤖 Croupier", font=("Arial", 13, "bold"), bg="#1e1e1e", fg="#FF7788").pack()
        if not self.bj_game_over:
            tk.Label(dealer_frame, text=format_hand(self.bot_hand, reveal_all=False), font=("Arial", 30),
                     bg="#1e1e1e", fg="white").pack()
            tk.Label(dealer_frame, text="Total : ?", font=("Arial", 12), bg="#1e1e1e", fg="red").pack()
        else:
            tk.Label(dealer_frame, text=format_hand(self.bot_hand), font=("Arial", 30), bg="#1e1e1e", fg="white").pack()
            tk.Label(dealer_frame, text=f"Total : {b_total}", font=("Arial", 12), bg="#1e1e1e", fg="red").pack()

        # Joueur (en bas)
        player_frame = tk.Frame(center_frame, bg="#1e1e1e")
        player_frame.pack(pady=10)
        tk.Label(player_frame, text="🧑‍💼 Toi", font=("Arial", 13, "bold"), bg="#1e1e1e", fg="#00FF88").pack()
        tk.Label(player_frame, text=format_hand(self.player_hands[self.active_hand]), font=("Arial", 30),
                 bg="#1e1e1e", fg="white").pack()
        tk.Label(player_frame, text=f"Total : {p_total}", font=("Arial", 12), bg="#1e1e1e", fg="lime").pack()

        # Gestion de la fin de partie
        if self.bj_game_over:
            return

        # Boutons d'action
        btn_frame = tk.Frame(center_frame, bg="#1e1e1e")
        btn_frame.pack(pady=15)

        # Hit et Stand toujours disponibles
        tk.Button(btn_frame, text="➕ Hit", font=("Arial", 12, "bold"), bg="#2e8b57", fg="white",
                  width=10, command=lambda: self.hit_blackjack(eco, uid)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="✅ Stand", font=("Arial", 12, "bold"), bg="#3399FF", fg="white",
                  width=10, command=lambda: self.stand_blackjack(eco, uid)).pack(side="left", padx=10)

        # Double disponible si main à 2 cartes et pas déjà doublée
        if len(self.player_hands[self.active_hand]) == 2 and not self.bj_doubled[self.active_hand]:
            tk.Button(btn_frame, text="✖️ Double", font=("Arial", 12, "bold"), bg="#FFD700", fg="black",
                      width=10, command=lambda: self.double_blackjack(eco, uid)).pack(side="left", padx=10)

        # Split disponible si main à 2 cartes identiques et max 4 mains
        hand = self.player_hands[self.active_hand]
        if len(hand) == 2 and hand[0] == hand[1] and len(self.player_hands) < 4:
            tk.Button(btn_frame, text="🔀 Split", font=("Arial", 12, "bold"), bg="#00FF88", fg="black",
                      width=10, command=lambda: self.split_blackjack(eco, uid)).pack(side="left", padx=10)

        # Vérifie si le joueur a fait un blackjack ou bust
        if p_total == 21:
            self.end_blackjack(eco, uid, "blackjack")
            return
        if p_total > 21:
            self.end_blackjack(eco, uid, "bust")
            return

        eco = load_economie()
        solde = get_balance(uid, eco)
        heure = datetime.now().strftime("%H:%M:%S")
        solde_lbl = tk.Label(self.content, text=f"💰 {solde} AC   🕒 {heure}", font=("Arial", 11, "bold"),
                             bg="#1e1e1e", fg="#FFD700", anchor="e")
        solde_lbl.pack(anchor="ne", padx=20, pady=5)

    def hit_blackjack(self, eco, uid):
        if self.bj_game_over:
            return
        self.player_hands[self.active_hand].append(self.deck.pop())
        self.show_blackjack_state(eco, uid)

    def stand_blackjack(self, eco, uid):
        if self.bj_game_over:
            return
        def calc_total(h): return self.calc_blackjack_total(h)
        while calc_total(self.bot_hand) < 17:
            self.bot_hand.append(self.deck.pop())
        self.end_blackjack(eco, uid)  # <-- retire "stand"

    def double_blackjack(self, eco, uid):
        if self.bj_game_over or len(self.player_hands) > 1:
            return
        self.bet_amounts[self.active_hand] *= 2
        self.hit_blackjack(eco, uid)
        self.stand_blackjack(eco, uid)

    def split_blackjack(self, eco, uid):
        if self.bj_game_over or len(self.player_hands) > 2:
            return
        new_hand = [self.player_hands[self.active_hand].pop(1)]
        self.player_hands.append(new_hand)
        self.bet_amounts.append(self.bet_amounts[self.active_hand])
        self.show_blackjack_state(eco, uid)

    def end_blackjack(self, eco, uid):
        self.bj_game_over = True
        p_totals = [self.calc_blackjack_total(hand) for hand in self.player_hands]
        b_total = self.calc_blackjack_total(self.bot_hand)
        results = []
        gains = []

        for i, p_total in enumerate(p_totals):
            if p_total > 21:
                gains.append(-self.bet_amounts[i])
                results.append("💥 Bust")
            elif b_total > 21 or p_total > b_total:
                gains.append(self.bet_amounts[i])
                results.append("🎉 Gagné")
            elif p_total == b_total:
                gains.append(0)
                results.append("🤝 Égalité")
            else:
                gains.append(-self.bet_amounts[i])
                results.append("❌ Perdu")

        # Affichage des résultats
        for i, result in enumerate(results):
            txt = f"Main {i+1} : {result} {'+' + str(gains[i]) + ' AC' if gains[i] > 0 else ''}"
            tk.Label(self.content, text=txt, font=("Helvetica", 16, "bold"), fg="#FFD700", bg="#1e1e1e").pack(pady=10)

        # Mise à jour des soldes
        for i, gain in enumerate(gains):
            update_balance(uid, gain, eco, f"Blackjack {'Main ' + str(i+1)}")

        tk.Button(self.content, text="🔄 Rejouer", bg="#333", fg="white",
                  font=("Arial", 12, "bold"), command=lambda: self.choisir_table_blackjack(eco, uid)).pack(pady=5)

    def lancer_spin_gui(self, eco: dict[str, Any], uid: str) -> None:
        self.clear_content()
        bet = int(self.bet_var.get())
        result = random.choice(["💰 Gagné", "💀 Perdu", "🎲 Jackpot"])
        gain = -bet if result == "💀 Perdu" else bet * 2 if result == "🎲 Jackpot" else -bet + int(bet * 1.3)

        update_balance(uid, gain, eco, f"Spin ➜ {result}")
        msg = f"🎡 Résultat : {result}\n{'+' if gain > 0 else ''}{gain} AC"
        tk.Label(self.content, text=msg, font=("Arial", 14), bg="#1e1e1e", fg="cyan").pack(pady=10)

    def lancer_guess_gui(self, eco: dict[str, Any], uid: str) -> None:
        self.clear_content()
        bet = int(self.bet_var.get())
        secret = random.randint(1, 10)

        tk.Label(self.content, text="🎯 Choisis un nombre (1–10)", font=("Arial", 12), bg="#1e1e1e", fg="white").pack(pady=5)
        entry = tk.Entry(self.content, bg="gray", fg="white")
        entry.pack(pady=5)

        def validate_guess():
            guess = int(entry.get())
            if guess == secret:
                update_balance(uid, bet * 2, eco, f"Guess ✅ Gagné : {guess}")
                msg = f"🔥 Bravo ! C'était {secret} ➜ +{bet * 2} AC"
            else:
                update_balance(uid, -bet, eco, f"Guess ❌ Raté : {guess}")
                msg = f"❌ Mauvais choix. C'était {secret} ➜ -{bet} AC"
            tk.Label(self.content, text=msg, bg="#1e1e1e", fg="orange", font=("Arial", 12)).pack(pady=8)

        tk.Button(self.content, text="🎯 Valider", bg="blue", fg="white", command=validate_guess).pack(pady=5)

    def load_config_hub(self):
        self.clear_content()
        self.active_tab = "config_hub"

        tk.Label(self.content, text="🛠️ Configuration des Hubs Vocaux", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)

        try:
            with open("data/hub_config.json", "r", encoding="utf-8") as f:
                hub_data = json.load(f)
        except:
            tk.Label(self.content, text="❌ Impossible de charger hub_config.json", fg="red", bg="#1e1e1e").pack()
            return

        for hub_id, hub in hub_data.items():
            frame = tk.Frame(self.content, bg="#2c2c2c", pady=8, padx=15)
            frame.pack(fill="x", padx=20, pady=6)

            main_name = self.bot.get_channel(hub["main_channel_id"]).name if self.bot.get_channel(hub["main_channel_id"]) else "❓"
            tk.Label(frame, text=f"📡 Hub : {main_name}", font=("Arial", 14, "bold"),
                     bg="#2c2c2c", fg="white").pack(anchor="w")

            tk.Label(frame, text=f"👑 Propriétaire : <@{hub['owner_id']}>", bg="#2c2c2c", fg="gray").pack(anchor="w")
            tk.Label(frame, text=f"🗂 Catégorie : {hub['category_id']}", bg="#2c2c2c", fg="gray").pack(anchor="w")

            mods = hub.get("moderators_ids", {})
            tk.Label(frame, text=f"🧑‍💼 Modérateurs ({len(mods)}):", font=("Arial", 11), bg="#2c2c2c", fg="#00FF88").pack(anchor="w", pady=5)

            for uid, perms in mods.items():
                tk.Label(frame, text=f"• <@{uid}> → {', '.join(perms)}", bg="#2c2c2c", fg="gray").pack(anchor="w")

            tk.Button(frame, text="🔧 Modifier les permissions", bg="blue", fg="white",
                      command=lambda uid=hub['owner_id'], hid=hub_id: self.modify_mod_permissions(uid, hid) if hasattr(self, "modify_mod_permissions") else None).pack(side="left", padx=5)
            tk.Button(frame, text="🗑️ Supprimer ce Hub", bg="red", fg="white",
                      command=lambda hid=hub_id: self.delete_hub(hid)).pack(side="left", padx=5)

    def delete_hub(self, hub_id):
        with open("data/hub_config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if hub_id in data:
            del data[hub_id]
            with open("data/hub_config.json", "w", encoding="utf-8") as f2:
                json.dump(data, f2, indent=4)
            messagebox.showinfo("Hub supprimé", f"Le hub {hub_id} a été supprimé.")
            self.load_config_hub()

    def load_casino_stats(self):
        self.clear_content()
        eco = load_economie()
        uid = str(self.bot.user.id)

        tk.Label(self.content, text="📈 Stats Casino • Arsenal Studio", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#33CCFF").pack(pady=10)

        # 💰 Solde actuel
        solde = get_balance(uid, eco)
        tk.Label(self.content, text=f"💰 Ton solde : {solde} ArsenalCoins", bg="#1e1e1e", fg="lime",
                 font=("Arial", 14)).pack(pady=8)

        # 🧠 Historique personnel
        tk.Label(self.content, text="🗂 Historique récent :", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=4)
        history = get_history(uid, eco)
        for h in reversed(history):
            txt = f"{h['date']} ➜ {h['jeu']} ➜ {'+' if h['gain']>0 else ''}{h['gain']} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="gray").pack(anchor="w")

        # 👑 Top joueurs
        tk.Label(self.content, text="👑 Top 5 joueurs : ", bg="#1e1e1e", fg="#FFD700",
                 font=("Arial", 12)).pack(pady=10)
        leaderboard = get_leaderboard(eco)

        for i, (user_id, balance) in enumerate(leaderboard, start=1):
            name = "Toi" if str(user_id) == uid else f"User#{str(user_id)[-5:]}"
            txt = f"{i}. {name} ➜ {balance} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="orange").pack(anchor="w")

        # 🧮 Résumé en chiffres
        summary_frame = tk.Frame(self.content, bg="#2c2c2c", pady=10)
        summary_frame.pack(fill="x", padx=30)

        cmd_stats = getattr(self.bot, "command_usage", {})
        total_cmds = sum(cmd_stats.values())
        unique_cmds = len(cmd_stats)
        top_cmds = sorted(cmd_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        info = {
            "📘 Commandes enregistrées": len(self.bot.tree.get_commands()),
            "🔢 Total d'exécutions": total_cmds,
            "🧠 Commandes uniques utilisées": unique_cmds,
            "🔝 Top commandes listées": len(top_cmds)
        }

        for k, v in info.items():
            box = tk.Frame(summary_frame, bg="#2c2c2c", padx=10, pady=8)
            box.pack(side="left", padx=15)
            tk.Label(box, text=k, font=("Arial", 10, "bold"), bg="#2c2c2c", fg="#FFD700").pack()
            tk.Label(box, text=str(v), font=("Consolas", 12), bg="#2c2c2c", fg="#00FF88").pack()

        # 🔝 Top 10 commandes les plus utilisées avec barres
        bar_frame = tk.Frame(self.content, bg="#1e1e1e")
        bar_frame.pack(pady=10)

        tk.Label(bar_frame, text="🏆 Top 10 Commandes", font=("Arial", 14), bg="#1e1e1e", fg="white").pack(pady=5)

        max_usage = top_cmds[0][1] if top_cmds else 1

        for cmd, count in top_cmds:
            bar_container = tk.Frame(bar_frame, bg="#1e1e1e")
            bar_container.pack(fill="x", padx=25, pady=4)

            tk.Label(bar_container, text=f"• /{cmd}", font=("Arial", 10), bg="#1e1e1e", fg="#FFDD00", width=20, anchor="w").pack(side="left")

            bar_width = int((count / max_usage) * 200)
            bar = tk.Frame(bar_container, bg="#00FF88", width=bar_width, height=14)
            bar.pack(side="left")

            tk.Label(bar_container, text=f"{count}×", font=("Consolas", 10), bg="#1e1e1e", fg="gray", width=6).pack(side="left")

        # 🔍 Commande spécifique à analyser
        tk.Label(self.content, text="🔎 Analyse individuelle :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)
        entry = tk.Entry(self.content, bg="gray", fg="white", width=30)
        entry.pack(pady=5)

        result_lbl = tk.Label(self.content, text="", bg="#1e1e1e", fg="cyan", font=("Consolas", 11))
        result_lbl.pack(pady=5)

        def check_command_usage():
            cmd = entry.get()
            count = cmd_stats.get(cmd, 0)
            total = total_cmds or 1
            pct = round((count / total) * 100, 2)
            result_lbl.config(text=f"/{cmd} ➜ {count} exécutions ({pct}%)")

        tk.Button(self.content, text="📊 Voir", command=check_command_usage, bg="#333", fg="white").pack(pady=5)

    def trigger_reboot(self):
        self.clear_content()
        self.active_tab = "reboot"
        tk.Label(self.content, text="🔄 Recharger un module", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        modules = [f for f in os.listdir("modules") if f.endswith(".py")]
        module_var = tk.StringVar(value=modules[0] if modules else "")
        option_menu = tk.OptionMenu(self.content, module_var, modules[0], *modules)
        option_menu.pack(pady=10)
        def reload_selected():
            mod = module_var.get()
            if mod and mod != "Aucun module":
                try:
                    import importlib
                    importlib.reload(__import__(f"modules.{mod[:-3]}"))
                    messagebox.showinfo("✅ Module rechargé", f"{mod} rechargé avec succès.")
                except Exception as e:
                    messagebox.showerror("❌ Erreur", str(e))
        tk.Button(self.content, text="Recharger", bg="#FFD700", fg="black", command=reload_selected).pack(pady=10)

    def load_changelog(self):
        self.clear_content()
        self.active_tab = "changelog"
        tk.Label(self.content, text="📜 Changelog Arsenal Studio", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        changelog_path = "data/changelog.txt"
        try:
            with open(changelog_path, "r", encoding="utf-8") as f:
                changelog = f.read()
        except Exception:
            changelog = "Aucun changelog trouvé."
        changelog_box = tk.Text(self.content, height=25, width=90, bg="#2c2c2c", fg="white", wrap="word")
        changelog_box.insert("1.0", changelog)
        changelog_box.config(state="disabled")
        changelog_box.pack(pady=10)
    
    def load_help(self):
        self.clear_content()
        self.active_tab = "help"
        tk.Label(self.content, text="❓ Aide Arsenal Studio", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        help_text = (
            "Bienvenue dans Arsenal Creator Studio !\n\n"
            "• Naviguez via la barre latérale pour accéder aux différents modules.\n"
            "• Utilisez le panneau de configuration pour personnaliser le bot.\n"
            "• Jouez à des jeux et consultez vos statistiques dans la section Casino.\n"
            "• Pour toute question ou bug, utilisez le panneau Bugs & Feedbacks.\n\n"
            "Besoin d'aide supplémentaire ? Contactez le support Discord."
        )
        help_box = tk.Text(self.content, height=15, width=80, bg="#2c2c2c", fg="white", wrap="word")
        help_box.insert("1.0", help_text)
        help_box.config(state="disabled")
        help_box.pack(pady=10)

    # Ajoute ici toutes les autres méthodes existantes (load_stats, load_config, load_bugs, manage_adc_whitelist, etc.)
    # ... (reprends le code de tes méthodes existantes, corrige les doublons et l'indentation)

    # Méthodes "à venir" pour éviter les erreurs
    def load_reel_pocket(self):
        self.clear_content()
        self.active_tab = "reel_pocket"
        tk.Label(self.content, text="🎲 Reel Pocket (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Reel Pocket n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_poker(self):
        self.clear_content()
        self.active_tab = "poker"
        tk.Label(self.content, text="🃏 Poker (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Poker n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_dungeon(self):
        self.clear_content()
        self.active_tab = "dungeon"
        tk.Label(self.content, text="🏹 Donjon RPG (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Donjon RPG n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_chat(self):
        self.clear_content()
        self.active_tab = "chat"
        tk.Label(self.content, text="💬 Chat Global (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Chat Global n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def show_shop_gui(self):
        self.clear_content()
        self.active_tab = "shop"
        tk.Label(self.content, text="🛒 Boutique Arsenal Studio", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La boutique n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_admin(self):
        self.clear_content()
        self.active_tab = "admin"
        tk.Label(self.content, text="🛠️ Panneau Admin (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Admin n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_modules(self):
        self.clear_content()
        self.active_tab = "modules"
        frame = tk.Frame(self.content, bg="#222244", bd=2, relief="groove")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text="🔄 Modules", font=("Helvetica", 22, "bold"), bg="#222244", fg="#FFD700").pack(pady=20)
        tk.Label(frame, text="Gestion des modules à venir !", bg="#222244", fg="white", font=("Arial", 14)).pack(pady=10)
        tk.Label(frame, text="Active/désactive, recharge, configure tes modules ici.", bg="#222244", fg="#00FF88", font=("Arial", 11)).pack(pady=10)
        tk.Button(frame, text="Retour", bg="#FFD700", fg="black", font=("Arial", 12, "bold"), command=self.load_dashboard).pack(pady=20)
    def load_logs(self):
        self.clear_content()
        self.active_tab = "logs"
        tk.Label(self.content, text="💬 Logs (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Logs n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_settings(self):
        self.clear_content()
        self.active_tab = "settings"
        tk.Label(self.content, text="⚙️ Paramètres (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La gestion des paramètres n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

    def load_discord_servers(self):
        self.clear_content()
        self.active_tab = "discord_servers"
        tk.Label(self.content, text="🌐 Liste des serveurs Discord (à venir)", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="La fonctionnalité Liste des serveurs Discord n'est pas encore disponible.", bg="#1e1e1e", fg="white",
                 font=("Arial", 12)).pack(pady=10)

def lancer_creator_interface(bot):
    panel = ArsenalCreatorPanel(bot)
    panel.mainloop()