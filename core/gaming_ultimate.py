# 🎮 Arsenal V4 Ultimate - Gaming sans Pygame (Compatible Render)

import random
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# ==================== GAMING ULTIMATE SANS PYGAME ====================

class GamingUltimate:
    """Module Gaming Ultimate optimisé pour Render (sans pygame)"""
    
    def __init__(self):
        self.games_data = {
            'users': {},  # Stats des joueurs
            'leaderboards': {},  # Classements
            'daily_challenges': {}  # Défis quotidiens
        }
        print("🎮 Gaming Ultimate initialisé (Mode Render - Sans Pygame)")
    
    # ==================== JEUX SIMPLES ====================
    
    async def coinflip(self, user_id: str, bet: int = 50) -> Dict[str, Any]:
        """Pile ou Face"""
        result = random.choice(['pile', 'face'])
        user_choice = random.choice(['pile', 'face'])  # Pour la démo
        won = result == user_choice
        
        return {
            'game': 'coinflip',
            'result': result,
            'user_choice': user_choice,
            'won': won,
            'bet': bet,
            'winnings': bet * 2 if won else 0,
            'message': f"🪙 {'Pile' if result == 'pile' else 'Face'}! {'Gagné!' if won else 'Perdu!'}"
        }
    
    async def dice_roll(self, user_id: str, bet: int = 50, target: int = 6) -> Dict[str, Any]:
        """Lancer de dés"""
        roll = random.randint(1, 6)
        won = roll >= target
        multiplier = 6 - target + 1  # Plus difficile = plus de gains
        
        return {
            'game': 'dice',
            'roll': roll,
            'target': target,
            'won': won,
            'bet': bet,
            'winnings': bet * multiplier if won else 0,
            'message': f"🎲 Vous avez fait {roll}! {'Gagné!' if won else 'Perdu!'}"
        }
    
    async def number_guessing(self, user_id: str, guess: int, bet: int = 100) -> Dict[str, Any]:
        """Deviner un nombre entre 1 et 100"""
        target = random.randint(1, 100)
        difference = abs(target - guess)
        
        if difference == 0:
            # Exact !
            won = True
            multiplier = 50
            message = f"🎯 PARFAIT! Le nombre était {target}!"
        elif difference <= 5:
            # Très proche
            won = True
            multiplier = 10
            message = f"🔥 Très proche! Le nombre était {target} (différence: {difference})"
        elif difference <= 10:
            # Proche
            won = True
            multiplier = 3
            message = f"👍 Proche! Le nombre était {target} (différence: {difference})"
        else:
            # Loin
            won = False
            multiplier = 0
            message = f"❌ Loin! Le nombre était {target} (différence: {difference})"
        
        return {
            'game': 'number_guessing',
            'guess': guess,
            'target': target,
            'difference': difference,
            'won': won,
            'bet': bet,
            'winnings': bet * multiplier if won else 0,
            'message': message
        }
    
    async def roulette(self, user_id: str, bet: int, choice: str) -> Dict[str, Any]:
        """Roulette simple"""
        numbers = list(range(37))  # 0-36
        result = random.choice(numbers)
        
        # Types de paris
        won = False
        multiplier = 0
        
        if choice.isdigit():
            # Pari sur un numéro
            if int(choice) == result:
                won = True
                multiplier = 35
        elif choice in ['rouge', 'red']:
            # Pari sur rouge (1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36)
            red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
            if result in red_numbers:
                won = True
                multiplier = 2
        elif choice in ['noir', 'black']:
            # Pari sur noir
            black_numbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
            if result in black_numbers:
                won = True
                multiplier = 2
        elif choice in ['pair', 'even']:
            # Pari sur pair
            if result != 0 and result % 2 == 0:
                won = True
                multiplier = 2
        elif choice in ['impair', 'odd']:
            # Pari sur impair
            if result != 0 and result % 2 == 1:
                won = True
                multiplier = 2
        
        return {
            'game': 'roulette',
            'result': result,
            'choice': choice,
            'won': won,
            'bet': bet,
            'winnings': bet * multiplier if won else 0,
            'message': f"🎰 Résultat: {result}! {'Gagné!' if won else 'Perdu!'}"
        }
    
    async def blackjack_simple(self, user_id: str, bet: int = 100) -> Dict[str, Any]:
        """BlackJack simplifié"""
        
        def card_value(cards):
            total = sum(cards)
            return total
        
        # Distribuer les cartes (valeurs simples 1-11)
        player_cards = [random.randint(1, 11), random.randint(1, 11)]
        dealer_cards = [random.randint(1, 11), random.randint(1, 11)]
        
        player_total = card_value(player_cards)
        dealer_total = card_value(dealer_cards)
        
        # Logique simplifiée
        if player_total == 21:
            # BlackJack joueur
            won = True
            multiplier = 2.5
            message = "🃏 BLACKJACK! Vous gagnez!"
        elif player_total > 21:
            # Joueur bust
            won = False
            multiplier = 0
            message = f"💥 BUST! Vous avez {player_total}"
        elif dealer_total > 21:
            # Dealer bust
            won = True
            multiplier = 2
            message = f"🎉 Le dealer a bust avec {dealer_total}! Vous gagnez!"
        elif player_total > dealer_total:
            # Joueur gagne
            won = True
            multiplier = 2
            message = f"🎉 Vous gagnez! {player_total} vs {dealer_total}"
        elif player_total == dealer_total:
            # Égalité
            won = True
            multiplier = 1
            message = f"🤝 Égalité! {player_total} vs {dealer_total}"
        else:
            # Dealer gagne
            won = False
            multiplier = 0
            message = f"😞 Le dealer gagne! {player_total} vs {dealer_total}"
        
        return {
            'game': 'blackjack',
            'player_cards': player_cards,
            'dealer_cards': dealer_cards,
            'player_total': player_total,
            'dealer_total': dealer_total,
            'won': won,
            'bet': bet,
            'winnings': int(bet * multiplier) if won else 0,
            'message': message
        }
    
    async def quiz_question(self, user_id: str, category: str = 'general') -> Dict[str, Any]:
        """Quiz culture générale"""
        
        questions = {
            'general': [
                {"question": "Quelle est la capitale de la France?", "answers": ["Paris", "Lyon", "Marseille", "Toulouse"], "correct": 0},
                {"question": "Combien de continents y a-t-il?", "answers": ["5", "6", "7", "8"], "correct": 2},
                {"question": "Quel est l'élément chimique de symbole O?", "answers": ["Or", "Oxygène", "Osmium", "Ozone"], "correct": 1},
                {"question": "En quelle année a eu lieu la Révolution française?", "answers": ["1789", "1792", "1799", "1804"], "correct": 0},
            ],
            'gaming': [
                {"question": "Quel jeu a popularisé le Battle Royale?", "answers": ["PUBG", "Fortnite", "Apex Legends", "Call of Duty"], "correct": 0},
                {"question": "Qui a créé Minecraft?", "answers": ["Notch", "Valve", "Epic Games", "Blizzard"], "correct": 0},
                {"question": "Quelle console a sorti Mario Bros?", "answers": ["PlayStation", "Xbox", "Nintendo", "Sega"], "correct": 2},
            ]
        }
        
        category_questions = questions.get(category, questions['general'])
        question_data = random.choice(category_questions)
        
        return {
            'game': 'quiz',
            'category': category,
            'question': question_data['question'],
            'answers': question_data['answers'],
            'correct_index': question_data['correct'],
            'reward': 150,  # Récompense de base
            'message': f"❓ Question {category}: {question_data['question']}"
        }
    
    async def slots_machine(self, user_id: str, bet: int = 50) -> Dict[str, Any]:
        """Machine à sous"""
        
        symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']
        weights = [30, 25, 20, 15, 7, 2, 1]  # Probabilités
        
        # Générer 3 symboles
        reels = random.choices(symbols, weights=weights, k=3)
        
        # Calculer les gains
        if reels[0] == reels[1] == reels[2]:
            # Triple
            if reels[0] == '7️⃣':
                multiplier = 100  # Jackpot!
                message = "🎰 JACKPOT! Triple 7!"
            elif reels[0] == '💎':
                multiplier = 50
                message = "💎 Triple diamant!"
            elif reels[0] == '🔔':
                multiplier = 25
                message = "🔔 Triple cloche!"
            else:
                multiplier = 10
                message = f"🎉 Triple {reels[0]}!"
            won = True
        elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
            # Double
            multiplier = 3
            message = "👍 Une paire!"
            won = True
        else:
            # Rien
            multiplier = 0
            message = "😞 Aucun gain..."
            won = False
        
        return {
            'game': 'slots',
            'reels': reels,
            'won': won,
            'bet': bet,
            'winnings': bet * multiplier if won else 0,
            'multiplier': multiplier,
            'message': f"🎰 {' '.join(reels)} - {message}"
        }
    
    # ==================== STATISTIQUES ====================
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Récupérer les stats d'un utilisateur"""
        if user_id not in self.games_data['users']:
            self.games_data['users'][user_id] = {
                'games_played': 0,
                'games_won': 0,
                'total_winnings': 0,
                'favorite_game': None,
                'achievements': [],
                'last_played': None
            }
        
        stats = self.games_data['users'][user_id]
        win_rate = (stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
        
        return {
            'user_id': user_id,
            'games_played': stats['games_played'],
            'games_won': stats['games_won'],
            'win_rate': round(win_rate, 1),
            'total_winnings': stats['total_winnings'],
            'favorite_game': stats['favorite_game'],
            'achievements': stats['achievements'],
            'last_played': stats['last_played']
        }
    
    async def update_user_stats(self, user_id: str, game_result: Dict[str, Any]):
        """Mettre à jour les stats d'un utilisateur"""
        if user_id not in self.games_data['users']:
            self.games_data['users'][user_id] = {
                'games_played': 0,
                'games_won': 0,
                'total_winnings': 0,
                'favorite_game': None,
                'achievements': [],
                'last_played': None
            }
        
        stats = self.games_data['users'][user_id]
        stats['games_played'] += 1
        if game_result.get('won', False):
            stats['games_won'] += 1
        stats['total_winnings'] += game_result.get('winnings', 0)
        stats['favorite_game'] = game_result.get('game', 'unknown')
        stats['last_played'] = datetime.now().isoformat()
        
        # Vérifier les achievements
        await self._check_achievements(user_id, stats)
    
    async def _check_achievements(self, user_id: str, stats: Dict[str, Any]):
        """Vérifier et débloquer les achievements"""
        achievements = stats['achievements']
        
        # Achievement: Premier jeu
        if stats['games_played'] == 1 and 'first_game' not in achievements:
            achievements.append('first_game')
        
        # Achievement: 10 victoires
        if stats['games_won'] >= 10 and 'winner_10' not in achievements:
            achievements.append('winner_10')
        
        # Achievement: 1000 AC gagnés
        if stats['total_winnings'] >= 1000 and 'rich_player' not in achievements:
            achievements.append('rich_player')
        
        # Achievement: 100 jeux joués
        if stats['games_played'] >= 100 and 'veteran' not in achievements:
            achievements.append('veteran')
    
    async def get_leaderboard(self, category: str = 'winnings') -> List[Dict[str, Any]]:
        """Récupérer le classement"""
        users_stats = []
        
        for user_id, stats in self.games_data['users'].items():
            user_data = {
                'user_id': user_id,
                'games_played': stats['games_played'],
                'games_won': stats['games_won'],
                'total_winnings': stats['total_winnings'],
                'win_rate': (stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
            }
            users_stats.append(user_data)
        
        # Trier selon la catégorie
        if category == 'winnings':
            users_stats.sort(key=lambda x: x['total_winnings'], reverse=True)
        elif category == 'games_played':
            users_stats.sort(key=lambda x: x['games_played'], reverse=True)
        elif category == 'win_rate':
            users_stats.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return users_stats[:10]  # Top 10

# ==================== INSTANCE GLOBALE ====================

# Instance globale (remplace pygame pour Render)
gaming_ultimate = GamingUltimate()

# ==================== FONCTIONS UTILITAIRES ====================

async def play_random_game(user_id: str, bet: int = 50) -> Dict[str, Any]:
    """Jouer un jeu aléatoire"""
    games = ['coinflip', 'dice', 'slots', 'roulette']
    game = random.choice(games)
    
    if game == 'coinflip':
        return await gaming_ultimate.coinflip(user_id, bet)
    elif game == 'dice':
        return await gaming_ultimate.dice_roll(user_id, bet)
    elif game == 'slots':
        return await gaming_ultimate.slots_machine(user_id, bet)
    elif game == 'roulette':
        return await gaming_ultimate.roulette(user_id, bet, random.choice(['rouge', 'noir', 'pair', 'impair']))

if __name__ == "__main__":
    # Test des jeux
    async def test_games():
        print("🎮 Test Gaming Ultimate (Sans Pygame)")
        
        # Test coinflip
        result = await gaming_ultimate.coinflip('test_user', 100)
        print(f"Coinflip: {result}")
        
        # Test slots
        result = await gaming_ultimate.slots_machine('test_user', 50)
        print(f"Slots: {result}")
        
        # Test quiz
        result = await gaming_ultimate.quiz_question('test_user')
        print(f"Quiz: {result}")
        
        # Stats
        await gaming_ultimate.update_user_stats('test_user', {'won': True, 'winnings': 100, 'game': 'test'})
        stats = await gaming_ultimate.get_user_stats('test_user')
        print(f"Stats: {stats}")
    
    asyncio.run(test_games())
