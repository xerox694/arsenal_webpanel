import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
import random
from datetime import datetime, timezone

ECONOMIE_PATH = "data/economie.json"
PROFILE_PATH = "data/profiles.json"
CHALLENGE_PATH = "data/challenges.json"

def load_economie():
    if os.path.exists(ECONOMIE_PATH):
        with open(ECONOMIE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_economie(data):
    with open(ECONOMIE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_profiles():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_profiles(data):
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_challenges():
    if os.path.exists(CHALLENGE_PATH):
        with open(CHALLENGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_challenges(data):
    with open(CHALLENGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class ArsenalMemberPanel(tk.Tk):
    def __init__(self, user_id, server_id, get_discord_data):
        super().__init__()
        self.user_id = str(user_id)
        self.server_id = str(server_id)
        self.get_discord_data = get_discord_data
        self.title("👤 Arsenal Member Panel")
        self.geometry("1200x800")
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
            ("Profil", [
                ("🏠 Dashboard", self.load_dashboard),
                ("👤 Mon profil", self.load_profile),
                ("🎖️ Succès & Challenges", self.load_challenges),
                ("📊 Statistiques", self.load_stats),
            ]),
            ("Economie", [
                ("💰 Mon solde", self.load_balance),
                ("🏆 Leaderboard", self.load_leaderboard),
                ("🗂 Historique", self.load_history),
            ]),
            ("Jeux", [
                ("🃏 Blackjack", self.load_blackjack),
                ("🎲 Roulette", self.load_roulette),
                ("🎯 Guess", self.load_guess),
                ("🖱️ Idle Clicker", self.load_idle_clicker),
                ("🏹 Donjon RPG", self.load_dungeon),
            ]),
            ("Social", [
                ("💬 Chat Global", self.load_chat),
                ("👥 Membres du serveur", self.load_members),
                ("🔗 Rôles du serveur", self.load_roles),
            ]),
            ("Divers", [
                ("📜 Changelog", self.load_changelog),
                ("❓ Aide", self.load_help),
                ("⚙️ Paramètres", self.load_settings),
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
        tk.Label(self.content, text="👤 Arsenal Member Dashboard", font=("Helvetica", 22, "bold"),
                 bg="#1e1e1e", fg="#00eaff").pack(pady=20)
        # Infos utilisateur
        profiles = load_profiles()
        profile = profiles.get(self.user_id, {
            "pseudo": "Inconnu",
            "xp": 0,
            "level": 1,
            "bio": "Aucune bio",
            "last_login": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })
        tk.Label(self.content, text=f"Pseudo : {profile.get('pseudo', 'Inconnu')}", bg="#1e1e1e", fg="white", font=("Arial", 13)).pack(pady=5)
        tk.Label(self.content, text=f"Niveau : {profile.get('level', 1)}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"XP : {profile.get('xp', 0)}", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Bio : {profile.get('bio', 'Aucune bio')}", bg="#1e1e1e", fg="#00eaff", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Dernière connexion : {profile.get('last_login', 'N/A')}", bg="#1e1e1e", fg="white", font=("Arial", 11)).pack(pady=2)
        tk.Label(self.content, text="Utilise la barre latérale pour explorer toutes les fonctionnalités !", bg="#1e1e1e", fg="gray", font=("Arial", 12)).pack(pady=15)

    def load_profile(self):
        self.clear_content()
        self.active_tab = "profile"
        profiles = load_profiles()
        profile = profiles.get(self.user_id, {
            "pseudo": "Inconnu",
            "xp": 0,
            "level": 1,
            "bio": "Aucune bio",
            "last_login": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })
        tk.Label(self.content, text="👤 Mon Profil", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text=f"Pseudo : {profile.get('pseudo', 'Inconnu')}", bg="#1e1e1e", fg="white", font=("Arial", 13)).pack(pady=5)
        tk.Label(self.content, text=f"Niveau : {profile.get('level', 1)}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"XP : {profile.get('xp', 0)}", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Bio : {profile.get('bio', 'Aucune bio')}", bg="#1e1e1e", fg="#00eaff", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Dernière connexion : {profile.get('last_login', 'N/A')}", bg="#1e1e1e", fg="white", font=("Arial", 11)).pack(pady=2)
        # Modification de la bio
        bio_var = tk.StringVar(value=profile.get('bio', ''))
        tk.Label(self.content, text="Modifier ma bio :", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Entry(self.content, textvariable=bio_var, width=60).pack(pady=5)
        def save_bio():
            profiles[self.user_id]["bio"] = bio_var.get()
            save_profiles(profiles)
            messagebox.showinfo("✅", "Bio mise à jour !")
            self.load_profile()
        tk.Button(self.content, text="Sauvegarder", bg="#FFD700", fg="black", command=save_bio).pack(pady=10)

    def load_challenges(self):
        self.clear_content()
        self.active_tab = "challenges"
        tk.Label(self.content, text="🎖️ Succès & Challenges", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        challenges = load_challenges().get(self.user_id, [])
        if not challenges:
            tk.Label(self.content, text="Aucun succès débloqué pour le moment.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)
        else:
            for ch in challenges:
                tk.Label(self.content, text=f"🏅 {ch['title']} : {ch['desc']}", bg="#1e1e1e", fg="#00FF88", font=("Arial", 12)).pack(pady=4)
        tk.Button(self.content, text="Actualiser", bg="#FFD700", fg="black", command=self.load_challenges).pack(pady=10)

    def load_stats(self):
        self.clear_content()
        self.active_tab = "stats"
        tk.Label(self.content, text="📊 Mes Statistiques", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#00eaff").pack(pady=15)
        eco = load_economie()
        user_data = eco.get(self.user_id, {"balance": 0, "history": []})
        tk.Label(self.content, text=f"Solde : {user_data['balance']} ArsenalCoins", bg="#1e1e1e", fg="lime", font=("Arial", 14)).pack(pady=8)
        tk.Label(self.content, text=f"Nombre de parties jouées : {len(user_data['history'])}", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=5)
        win_count = sum(1 for h in user_data["history"] if h["gain"] > 0)
        lose_count = sum(1 for h in user_data["history"] if h["gain"] < 0)
        tk.Label(self.content, text=f"Victoires : {win_count}", bg="#1e1e1e", fg="#FFD700", font=("Arial", 12)).pack(pady=2)
        tk.Label(self.content, text=f"Défaites : {lose_count}", bg="#1e1e1e", fg="#FF5555", font=("Arial", 12)).pack(pady=2)
        tk.Button(self.content, text="Actualiser", bg="#FFD700", fg="black", command=self.load_stats).pack(pady=10)

    def load_balance(self):
        self.clear_content()
        self.active_tab = "balance"
        eco = load_economie()
        user_data = eco.get(self.user_id, {"balance": 0, "history": []})
        tk.Label(self.content, text="💰 Mon Solde", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text=f"Solde actuel : {user_data['balance']} ArsenalCoins", bg="#1e1e1e", fg="lime", font=("Arial", 14)).pack(pady=8)
        tk.Button(self.content, text="Actualiser", bg="#FFD700", fg="black", command=self.load_balance).pack(pady=10)

    def load_leaderboard(self):
        self.clear_content()
        self.active_tab = "leaderboard"
        tk.Label(self.content, text="🏆 Leaderboard Global", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        eco = load_economie()
        leaderboard = sorted(eco.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
        for i, (uid, data) in enumerate(leaderboard, start=1):
            name = f"User#{str(uid)[-5:]}" if str(uid) != str(self.user_id) else "Toi"
            txt = f"{i}. {name} ➜ {data['balance']} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="orange").pack(anchor="w")

    def load_history(self):
        self.clear_content()
        self.active_tab = "history"
        eco = load_economie()
        user_data = eco.get(self.user_id, {"balance": 0, "history": []})
        tk.Label(self.content, text="🗂 Historique de mes parties", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        for h in reversed(user_data["history"][-20:]):
            txt = f"{h['date']} ➜ {h['jeu']} ➜ {'+' if h['gain']>0 else ''}{h['gain']} AC"
            tk.Label(self.content, text=txt, bg="#1e1e1e", fg="gray").pack(anchor="w")

    # Jeux
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

    def load_idle_clicker(self):
        self.clear_content()
        self.active_tab = "idle_clicker"
        tk.Label(self.content, text="🖱️ Idle Clicker", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : Idle Clicker avec upgrades, boosts, etc.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

    def load_dungeon(self):
        self.clear_content()
        self.active_tab = "dungeon"
        tk.Label(self.content, text="🏹 Donjon RPG", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : Donjon RPG avec stuff, gemmes, boss, XP, etc.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

    # Social
    def load_chat(self):
        self.clear_content()
        self.active_tab = "chat"
        tk.Label(self.content, text="💬 Chat Global", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#00eaff").pack(pady=15)
        tk.Label(self.content, text="Fonctionnalité à venir : chat global entre membres.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

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
        tk.Label(self.content, text="🔗 Rôles du serveur", font=("Helvetica", 20, "bold"),
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

    # Divers
    def load_changelog(self):
        self.clear_content()
        self.active_tab = "changelog"
        tk.Label(self.content, text="📜 Changelog Arsenal Member Panel", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        changelog = (
            "V1.0 - Création du panel membre\n"
            "V1.1 - Ajout profil, stats, leaderboard\n"
            "V1.2 - Jeux connectés à la base Creator\n"
            "V1.3 - Succès & challenges\n"
            "V1.4 - Social et affichage membres/roles\n"
        )
        tk.Label(self.content, text=changelog, bg="#1e1e1e", fg="white", font=("Arial", 12), justify="left", anchor="w").pack(pady=10)

    def load_help(self):
        self.clear_content()
        self.active_tab = "help"
        tk.Label(self.content, text="❓ Centre d'aide Member Panel", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        help_txt = (
            "Ce panel te permet de profiter de toutes les fonctionnalités Arsenal en tant que membre.\n"
            "• Dashboard : infos profil et stats\n"
            "• Profil : pseudo, bio, XP, niveau\n"
            "• Succès : challenges et succès débloqués\n"
            "• Economie : solde, historique, leaderboard\n"
            "• Jeux : blackjack, roulette, idle clicker, donjon RPG\n"
            "• Social : chat global, membres, rôles\n"
            "Tout est synchronisé avec la base Creator pour une expérience fluide !"
        )
        tk.Label(self.content, text=help_txt, bg="#1e1e1e", fg="white", font=("Arial", 12), justify="left", anchor="w").pack(pady=10)

    def load_settings(self):
        self.clear_content()
        self.active_tab = "settings"
        tk.Label(self.content, text="⚙️ Paramètres", font=("Helvetica", 20, "bold"),
                 bg="#1e1e1e", fg="#FFD700").pack(pady=15)
        tk.Label(self.content, text="Personnalisation à venir : thème, notifications, etc.", bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(pady=10)

def lancer_member_interface(user_id, server_id, get_discord_data):
    app = ArsenalMemberPanel(user_id, server_id, get_discord_data)
    app.mainloop()