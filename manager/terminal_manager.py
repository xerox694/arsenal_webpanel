import asyncio
import sys
from core.logger import log

async def start_terminal(client):
    """
    Terminal interactif en ligne.
    Tape des commandes pendant que le bot tourne : status, say, exit, reload...
    """
    log.info("[TERMINAL] Terminal prêt. Tape une commande :")

    while True:
        cmd = await asyncio.to_thread(input, "> ")

        if cmd.lower() in ["exit", "quit"]:
            log.info("[TERMINAL] Fermeture du bot demandée.")
            await client.close()
            sys.exit()

        elif cmd.lower() == "status":
            name = client.user.name if client.user else "❓"
            guilds = len(client.guilds)
            uptime = str((discord.utils.utcnow() - client.startup_time)).split('.')[0]
            print(f"🧠 Bot : {name} | Serveurs : {guilds} | Uptime : {uptime}")

        elif cmd.lower().startswith("say "):
            msg = cmd[4:].strip()
            log.info(f"[TERMINAL] Message simulé : {msg}")

        elif cmd.lower() == "reload_config":
            try:
                from manager.config_manager import load_config
                load_config()
                print("🔄 Config rechargée.")
            except Exception as e:
                print(f"❌ Erreur reload config : {e}")

        elif cmd.lower() == "list_modules":
            import os
            folders = ["commands", "managers", "modules"]
            for folder in folders:
                try:
                    files = os.listdir(folder)
                    print(f"{folder}/ ➜ {len(files)} fichiers")
                    for f in files:
                        print(f" - {f}")
                except:
                    print(f"❌ Dossier introuvable : {folder}")

        elif cmd.lower() == "help":
            print("""
📘 Commandes terminal disponibles :
- status → info sur le bot
- say <texte> → simule un message
- reload_config → recharge config.json
- list_modules → affiche fichiers
- exit / quit → ferme le bot
""")

        else:
            print(f"❌ Commande inconnue : {cmd} | Tape 'help' pour la liste")