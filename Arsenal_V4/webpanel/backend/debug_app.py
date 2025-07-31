#!/usr/bin/env python3
"""Script pour identifier où le code app.py plante"""

print("🔍 Test ligne par ligne du fichier app.py...")

import traceback

try:
    # Lire le fichier ligne par ligne et l'exécuter
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    code_so_far = ""
    for i, line in enumerate(lines, 1):
        code_so_far += line
        
        # Tester l'exécution à chaque ajout significatif
        if line.strip() and not line.strip().startswith('#'):
            try:
                # Créer un namespace pour l'exécution
                namespace = {}
                exec(code_so_far, namespace)
                
                # Vérifier si app et socketio sont définis
                if 'app' in namespace:
                    print(f"✅ Ligne {i}: Variable 'app' définie")
                if 'socketio' in namespace:
                    print(f"✅ Ligne {i}: Variable 'socketio' définie")
                    
            except SyntaxError as e:
                # Ignorer les erreurs de syntaxe (code incomplet)
                continue
            except Exception as e:
                print(f"❌ Erreur à la ligne {i}: {line.strip()}")
                print(f"   Erreur: {e}")
                # Continuer pour voir s'il y a d'autres erreurs
                break
    
    print("🎉 Analyse terminée!")
    
except Exception as e:
    print(f"❌ Erreur lors de l'analyse: {e}")
    traceback.print_exc()
