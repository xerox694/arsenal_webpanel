import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
from datetime import datetime, timezone

# Chemin vers la base de données partagée
ECONOMIE_PATH = "data/economie.json"
SERVER_CONFIG_PATH = "data/server_config.json"

def load_economie():
    if os.path.exists(ECONOMIE_PATH):
        with open(ECONOMIE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_economie(data):
    with open(ECONOMIE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_server_config():
    if os.path.exists(SERVER_CONFIG_PATH):
        with open(SERVER_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_server_config(data):
    with open(SERVER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class ArsenalAdminPanel(tk.Tk):
    def __init__(self, user_id, server_id, get_discord_data):
        super().__init__()
        self.user_id = user_id
        self.server_id = server_id
        self.get_discord_data = get_discord_data  # fonction pour récupérer membres, rôles, etc.
        self.title("🛡️ Arsenal Admin Panel")
        self.geometry("1200x750")
        self.configure(bg="#181c24")
        self.sidebar = tk.Frame(self, bg="#232a36", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg="#1e1e1e")
        self.content.pack(side="right", expand=True, fill="both")
        self.active_tab = None
        self.build_sidebar()
        self.load_dashboard()

    def build_sidebar(self):
        def switch(tab_func):
            tab_func()
        sections = [
            ("Serveur", [
                ("🏠 Dashboard", self.load_dashboard),
                ("👥 Membres", self.load_members),
                ("🔗 Rôles", self.load_roles),
                ("⚙️ Config serveur", self.load_server_config_gui),
                ("📊 Statistiques", self.load_stats),
            ]),
            ("Jeux", [
                ("🃏 Blackjack", self.load_blackjack),
                ("🎲 Roulette", self.load_roulette),
                ("🎯 Guess", self.load_guess),
                ("🏹 Donjon RPG", self.load_dungeon),
            ]),
            ("Economie", [
                ("💰 Solde & Transactions", self.load_economie_gui),
                ("🏆 Leaderboard", self.load_leaderboard),
            ]),
            ("Divers", [
                ("📜 Changelog", self.load_changelog),
                ("❓ Aide", self.load_help),
            ])
        ]
        for section, btns in sections:
            tk.Label(self.sidebar, text=section, fg="#00eaff", bg="#232a36", font=("Arial", 11, "bold")).pack(pady=(18, 4))
            for label, func in btns:
                tk.Button(self.sidebar, text=label, font=("Arial", 11, "bold"),
                          fg="white", bg="#00eaff", activebackground="#232a36",
                          relief="groove", bd=2, highlightbackground="#00eaff",
                          highlightthickness=2, command=lambda f=func: switch(f)
                ).pack(fill="x", pady=4)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def load_dashboard(self):
        self.clear_content()
        self.active_tab = "dashboard"
        tk.Label(self.content, text="🛡️ Arsenal Admin Dashboard", font=("Helvetica", 22, "bold"),
                 bg="#1e1e1e", fg="#00eaff").pack(pady=20)
        # Infos serveur
        server_data = self.get_discord_data(self.server_id)
        tk.Label(self.content, text=f"Nom du serveur : {server_data.get('name', 'Inconnu')}", bg="#1e1e1e", fg="white", font=("Arial", 13)).pack(pady=5)
        tk.Label(self.content, text=f"ID : {self.server_id}", bg="#1e1e1e", fg="gray", font=("Arial", 11)).pack(pady=2)
        tk.Label(self.content, text=f"Membres : {len(server_data.get('members', []))}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Rôles : {len(server_data.get('roles', []))}", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Fondateur : {server_data.get('owner', 'Inconnu')}", bg="#1e1e1e", fg="#00eaff", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Date de création : {server_data.get('created_at', 'N/A')}", bg="#1e1e1e", fg="white", font=("Arial", 11)).pack(pady=2)
        tk.Label(self.content, text="Utilise la barre latérale pour gérer ton serveur et jouer !", bg="#1e1e1e", fg="gray", font=("Arial", 12)).pack(pady=15)

    def load_members(self):
        self.clear_content()
        self.active_tab = "members"
        tk.Label(self.content, text="👥 Membres du serveur", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        server_data = self.get_discord_data(self.server_id)
        members = server_data.get("members", [])
        tree = ttk.Treeview(self.content, columns=("ID", "Nom", "Rôle", "Join"), show="headings", height=20)
        tree.heading("ID", text="ID")
        tree.heading("Nom", text="Nom")
        tree.heading("Rôle", text="Rôle principal")
        tree.heading("Join", text="Date d'arrivée")
        for m in members:
            tree.insert("", "end", values=(m["id"], m["name"], m.get("main_role", "Aucun"), m.get("joined_at", "N/A")))
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Button(self.content, text="Actualiser", bg="#FFD700", fg="black", command=self.load_members).pack(pady=10)

    def load_roles(self):
        self.clear_content()
        self.active_tab = "roles"
        tk.Label(self.content, text="🔗 Gestion des rôles", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#00eaff").pack(pady=15)
        server_data = self.get_discord_data(self.server_id)
        roles = server_data.get("roles", [])
        tree = ttk.Treeview(self.content, columns=("ID", "Nom", "Membres"), show="headings", height=15)
        tree.heading("ID", text="ID")
        tree.heading("Nom", text="Nom")
        tree.heading("Membres", text="Nb membres")
        for r in roles:
            tree.insert("", "end", values=(r["id"], r["name"], r.get("count", 0)))
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Button(self.content, text="Actualiser", bg="#FFD700", fg="black", command=self.load_roles).pack(pady=10)

    def load_server_config_gui(self):
        self.clear_content()
        self.active_tab = "server_config"
        tk.Label(self.content, text="⚙️ Configuration du serveur", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        config = load_server_config().get(str(self.server_id), {})
        tk.Label(self.content, text=f"Prefix : {config.get('prefix', '!')}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Salon d'accueil : {config.get('welcome_channel', 'Non défini')}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Salon logs : {config.get('log_channel', 'Non défini')}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Auto rôle : {config.get('auto_role', 'Aucun')}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Protection anti-raid : {'Activée' if config.get('anti_raid', False) else 'Désactivée'}", bg="#1e1e1e", fg="#FF5555", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.content, text="Modifier la config", bg="#FFD700", fg="black", command=self.edit_server_config).pack(pady=10)

    def edit_server_config(self):
        # Fenêtre de modification (exemple simplifié)
        top = tk.Toplevel(self)
        top.title("Modifier la config serveur")
        top.geometry("400x350")
        config = load_server_config().get(str(self.server_id), {})
        prefix_var = tk.StringVar(value=config.get("prefix", "!"))
        tk.Label(top, text="Prefix :", font=("Arial", 12)).pack(pady=5)
        tk.Entry(top, textvariable=prefix_var).pack(pady=5)
        def save():
            all_config = load_server_config()
            all_config[str(self.server_id)] = {
                "prefix": prefix_var.get(),
                # Ajoute ici les autres champs à sauvegarder
            }
            save_server_config(all_config)
            messagebox.showinfo("✅", "Configuration sauvegardée !")
            top.destroy()
            self.load_server_config_gui()
        tk.Button(top, text="Sauvegarder", bg="#FFD700", fg="black", command=save).pack(pady=15)

    def load_stats(self):
        self.clear_content()
        self.active_tab = "stats"
        tk.Label(self.content, text="📊 Statistiques Serveur", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#00eaff").pack(pady=15)
        server_data = self.get_discord_data(self.server_id)
        tk.Label(self.content, text=f"Membres : {len(server_data.get('members', []))}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Rôles : {len(server_data.get('roles', []))}", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Commandes utilisées : {server_data.get('commands_used', 0)}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Jeux lancés : {server_data.get('games_played', 0)}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.content, text=f"Date de création : {server_data.get('created_at', 'N/A')}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)

    def load_economie_gui(self):
        self.clear_content()
        self.active_tab = "economie"
        tk.Label(self.content, text="💰 Economie Serveur", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        eco = load_economie()
        user_data = eco.get(str(self.user_id), {"balance": 0, "history": []})
        tk.Label(self.content, text=f"Ton solde : {user_data['balance']} ArsenalCoins", bg="#1e1e1e", fg="lime", font=("Arial", 14)).pack(pady=8)
        tk.Label(self.content, text="Historique :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=4)
        for h in reversed(user_data["history"][-10:]):
            txt = f"{h['date']} ➜ {h['jeu']} ➜ {'+' if h['gain']>0 else ''}{h['gain']} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="gray").pack(anchor="w")

    def load_leaderboard(self):
        self.clear_content()
        self.active_tab = "leaderboard"
        tk.Label(self.content, text="🏆 Leaderboard Serveur", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        eco = load_economie()
        leaderboard = sorted(eco.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
        for i, (uid, data) in enumerate(leaderboard, start=1):
            name = f"User#{str(uid)[-5:]}" if str(uid) != str(self.user_id) else "Toi"
            txt = f"{i}. {name} ➜ {data['balance']} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="orange").pack(anchor="w")

    # Jeux (Blackjack, Roulette, Guess, Donjon RPG)
    def load_blackjack(self):
        self.clear_content()
        self.active_tab = "blackjack"
        tk.Label(self.content, text="🃏 Blackjack", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : jeu de Blackjack avec base partagée.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

    def load_roulette(self):
        self.clear_content()
        self.active_tab = "roulette"
        tk.Label(self.content, text="🎲 Roulette", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : jeu de Roulette avec base partagée.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

    def load_guess(self):
        self.clear_content()
        self.active_tab = "guess"
        tk.Label(self.content, text="🎯 Guess", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : jeu de Guess avec base partagée.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

    def load_dungeon(self):
        self.clear_content()
        self.active_tab = "dungeon"
        tk.Label(self.content, text="🏹 Donjon RPG", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : Donjon RPG avec stuff, gemmes, boss, XP, etc.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

    def load_changelog(self):
        self.clear_content()
        self.active_tab = "changelog"
        tk.Label(self.content, text="📜 Changelog Arsenal Admin Panel", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        changelog = (
            "V1.0 - Création du panel admin\n"
            "V1.1 - Ajout gestion membres et rôles\n"
            "V1.2 - Jeux connectés à la base Creator\n"
            "V1.3 - Statistiques et leaderboard\n"
            "V1.4 - Configuration serveur avancée\n"
        )
        tk.Label(self.content, text=changelog, bg="#1e1e1e", fg="white", font=("Arial", 12), justify="left", anchor="w").pack(pady=10)

    def load_help(self):
        self.clear_content()
        self.active_tab = "help"
        tk.Label(self.content, text="❓ Centre d'aide Admin Panel", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        help_txt = (
            "Ce panel te permet de gérer ton serveur Discord sans toucher au bot.\n"
            "• Dashboard : infos serveur et utilisateur\n"
            "• Membres : liste, rôles, dates d'arrivée\n"
            "• Rôles : gestion, nombre de membres\n"
            "• Config serveur : prefix, salons, auto rôle, protection\n"
            "• Jeux : accès aux jeux du Creator Panel\n"
            "• Economie : solde, historique, leaderboard\n"
            "Tout est synchronisé avec la base Creator pour une expérience fluide !"
        )
        tk.Label(self.content, text=help_txt, bg="#1e1e1e", fg="white", font=("Arial", 12), justify="left", anchor="w").pack(pady=10)

def lancer_admin_interface(user_id, server_id, get_discord_data):
    app = ArsenalAdminPanel(user_id, server_id, get_discord_data)
    app.mainloop()