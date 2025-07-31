#!/usr/bin/env python3
"""
🎉 DÉMONSTRATION - HUNT ROYAL ÉCONOMIE RÉELLE
=============================================

Ce script montre le nouveau système économique Hunt Royal
qui remplace le faux système de "rareté" par la vraie économie du jeu.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.hunt_royal_system import HuntRoyalDatabase
    
    print("🏹 HUNT ROYAL - ÉCONOMIE RÉELLE")
    print("=" * 50)
    
    db = HuntRoyalDatabase()
    hunters = db.get_all_hunters()
    
    print(f"✅ {len(hunters)} chasseurs dans la base de données")
    print()
    
    # Grouper par type de coût
    coins_hunters = [h for h in hunters if h['cost_type'] == 'coins']
    gems_hunters = [h for h in hunters if h['cost_type'] == 'gems'] 
    special_hunters = [h for h in hunters if h['cost_type'] == 'special']
    
    print("🪙 CHASSEURS GRATUITS/COINS")
    print("-" * 30)
    for hunter in coins_hunters:
        tier = hunter['tier_meta']
        pop = hunter['popularity']
        cost = hunter['cost_amount']
        print(f"• {hunter['name']} - {cost} coins (Tier {tier}, Pop {pop}%)")
    
    print("\n💎 CHASSEURS PREMIUM/GEMS")
    print("-" * 30)
    for hunter in gems_hunters:
        tier = hunter['tier_meta']
        pop = hunter['popularity']
        cost = hunter['cost_amount']
        print(f"• {hunter['name']} - {cost} gems (Tier {tier}, Pop {pop}%)")
    
    print("\n⭐ CHASSEURS ÉVÉNEMENTS/SPÉCIAUX")
    print("-" * 35)
    for hunter in special_hunters:
        tier = hunter['tier_meta']
        pop = hunter['popularity']
        cost = hunter['cost_amount']
        print(f"• {hunter['name']} - {cost} event tokens (Tier {tier}, Pop {pop}%)")
    
    print("\n" + "=" * 50)
    print("🎯 RÉSUMÉ DE L'ÉCONOMIE HUNT ROYAL")
    print("=" * 50)
    print("✅ PLUS de fausses raretés (Common/Rare/Epic/Legendary)")
    print("✅ Vraie économie du jeu (coins/gems/special)")
    print("✅ Tiers Meta basés sur la performance réelle")
    print("✅ Popularité communautaire en pourcentage")
    print("✅ Coûts d'achat réalistes")
    print()
    print("🏆 Tier S+/S = Chasseurs meta dominants")
    print("🥈 Tier A+/A = Chasseurs viables et forts") 
    print("🥉 Tier B+/B = Chasseurs corrects")
    print("📉 Tier C+/C = Chasseurs faibles/situationnels")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
