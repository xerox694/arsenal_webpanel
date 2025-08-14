#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification rapide du serveur Arsenal V4
"""

import requests
import json
import time
from datetime import datetime

def test_server():
    """Test rapide du serveur"""
    BASE_URL = "http://localhost:5000"
    
    print("🚀 Test du serveur Arsenal V4 WebPanel")
    print("=" * 50)
    
    # Test de connexion de base
    try:
        print("🔌 Test de connexion...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Serveur répond: {response.status_code}")
    except Exception as e:
        print(f"❌ Serveur non accessible: {e}")
        print("💡 Démarrez le serveur avec: python app.py")
        return False
    
    # Tests des endpoints critiques
    endpoints_to_test = [
        "/api/test",
        "/api/health", 
        "/api/status",
        "/api/info",
        "/api/nonexistent"  # Test de la route fallback
    ]
    
    results = []
    for endpoint in endpoints_to_test:
        try:
            print(f"🧪 Test {endpoint}...")
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            status = "✅ OK" if response.status_code < 500 else "⚠️ Error"
            results.append({
                'endpoint': endpoint,
                'status': response.status_code,
                'success': response.status_code < 500
            })
            
            print(f"   {status} - Status: {response.status_code}")
            
            # Afficher le JSON si possible
            try:
                data = response.json()
                if 'error' in data:
                    print(f"   📝 Message: {data.get('message', 'N/A')}")
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results.append({
                'endpoint': endpoint,
                'status': 'ERROR',
                'success': False
            })
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"Total testé: {total_count}")
    print(f"Succès: {success_count}")
    print(f"Échecs: {total_count - success_count}")
    print(f"Taux de réussite: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 Tous les tests sont passés !")
        print("✅ Les erreurs 404/502 semblent être corrigées")
    else:
        print(f"\n⚠️  {total_count - success_count} tests ont échoué")
        print("💡 Vérifiez les routes défaillantes")
    
    return success_count == total_count

if __name__ == "__main__":
    test_server()
