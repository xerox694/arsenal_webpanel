#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de Casino pour Arsenal_V4 WebPanel
Jeux: Blackjack, Poker, Roulette, Machine à Sous
"""

import random
import json
from datetime import datetime

class CasinoSystem:
    def __init__(self):
        self.games = {
            'blackjack': BlackjackGame(),
            'poker': PokerGame(),
            'roulette': RouletteGame(),
            'slots': SlotMachine()
        }
    
    def get_user_balance(self, user_id):
        """Récupérer le solde de l'utilisateur"""
        # TODO: Intégrer avec la base de données
        return 1000  # Solde par défaut
    
    def update_user_balance(self, user_id, amount):
        """Mettre à jour le solde de l'utilisateur"""
        # TODO: Intégrer avec la base de données
        pass

class BlackjackGame:
    def __init__(self):
        self.active_games = {}
    
    def start_game(self, user_id, bet_amount):
        """Commencer une partie de Blackjack"""
        deck = self._create_deck()
        random.shuffle(deck)
        
        # Distribuer les cartes
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        game_state = {
            'game_id': f"bj_{user_id}_{datetime.now().timestamp()}",
            'user_id': user_id,
            'bet_amount': bet_amount,
            'deck': deck,
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'status': 'playing',
            'created_at': datetime.now().isoformat()
        }
        
        self.active_games[game_state['game_id']] = game_state
        
        # Vérifier blackjack naturel
        if self._calculate_hand_value(player_hand) == 21:
            return self._end_game(game_state['game_id'], 'blackjack')
        
        return {
            'success': True,
            'game_id': game_state['game_id'],
            'player_hand': player_hand,
            'dealer_visible_card': dealer_hand[0],
            'player_value': self._calculate_hand_value(player_hand),
            'status': 'playing'
        }
    
    def hit(self, game_id):
        """Piocher une carte"""
        if game_id not in self.active_games:
            return {'success': False, 'error': 'Partie non trouvée'}
        
        game = self.active_games[game_id]
        if game['status'] != 'playing':
            return {'success': False, 'error': 'Partie terminée'}
        
        # Piocher une carte
        card = game['deck'].pop()
        game['player_hand'].append(card)
        
        player_value = self._calculate_hand_value(game['player_hand'])
        
        if player_value > 21:
            return self._end_game(game_id, 'bust')
        elif player_value == 21:
            return self._end_game(game_id, 'player_21')
        
        return {
            'success': True,
            'card': card,
            'player_hand': game['player_hand'],
            'player_value': player_value,
            'status': 'playing'
        }
    
    def stand(self, game_id):
        """Rester avec la main actuelle"""
        if game_id not in self.active_games:
            return {'success': False, 'error': 'Partie non trouvée'}
        
        game = self.active_games[game_id]
        
        # Le dealer joue
        dealer_hand = game['dealer_hand']
        deck = game['deck']
        
        while self._calculate_hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
        
        dealer_value = self._calculate_hand_value(dealer_hand)
        player_value = self._calculate_hand_value(game['player_hand'])
        
        # Déterminer le gagnant
        if dealer_value > 21:
            return self._end_game(game_id, 'dealer_bust')
        elif player_value > dealer_value:
            return self._end_game(game_id, 'player_wins')
        elif dealer_value > player_value:
            return self._end_game(game_id, 'dealer_wins')
        else:
            return self._end_game(game_id, 'tie')
    
    def _create_deck(self):
        """Créer un jeu de 52 cartes"""
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    
    def _calculate_hand_value(self, hand):
        """Calculer la valeur d'une main"""
        value = 0
        aces = 0
        
        for card in hand:
            rank = card['rank']
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                aces += 1
                value += 11
            else:
                value += int(rank)
        
        # Ajuster pour les As
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def _end_game(self, game_id, result):
        """Terminer la partie et calculer les gains"""
        game = self.active_games[game_id]
        bet = game['bet_amount']
        
        winnings = 0
        if result == 'blackjack':
            winnings = bet * 2.5  # Blackjack paye 3:2
        elif result in ['player_wins', 'player_21', 'dealer_bust']:
            winnings = bet * 2
        elif result == 'tie':
            winnings = bet  # Remboursement
        
        game['status'] = 'finished'
        game['result'] = result
        game['winnings'] = winnings
        
        return {
            'success': True,
            'result': result,
            'winnings': winnings,
            'player_hand': game['player_hand'],
            'dealer_hand': game['dealer_hand'],
            'player_value': self._calculate_hand_value(game['player_hand']),
            'dealer_value': self._calculate_hand_value(game['dealer_hand'])
        }

class RouletteGame:
    def __init__(self):
        self.numbers = list(range(0, 37))  # 0-36 (Roulette européenne)
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    def spin(self, bets):
        """Faire tourner la roulette"""
        winning_number = random.choice(self.numbers)
        results = []
        total_winnings = 0
        
        for bet in bets:
            bet_type = bet['type']
            bet_amount = bet['amount']
            bet_value = bet.get('value')
            
            winnings = self._calculate_winnings(bet_type, bet_value, bet_amount, winning_number)
            total_winnings += winnings
            
            results.append({
                'bet_type': bet_type,
                'bet_value': bet_value,
                'bet_amount': bet_amount,
                'winnings': winnings,
                'won': winnings > 0
            })
        
        return {
            'success': True,
            'winning_number': winning_number,
            'winning_color': self._get_color(winning_number),
            'bets': results,
            'total_winnings': total_winnings
        }
    
    def _calculate_winnings(self, bet_type, bet_value, bet_amount, winning_number):
        """Calculer les gains selon le type de pari"""
        if bet_type == 'number' and bet_value == winning_number:
            return bet_amount * 36  # Plein paye 35:1
        elif bet_type == 'color':
            if (bet_value == 'red' and winning_number in self.red_numbers) or \
               (bet_value == 'black' and winning_number in self.black_numbers):
                return bet_amount * 2
        elif bet_type == 'even_odd':
            if (bet_value == 'even' and winning_number % 2 == 0 and winning_number != 0) or \
               (bet_value == 'odd' and winning_number % 2 == 1):
                return bet_amount * 2
        elif bet_type == 'high_low':
            if (bet_value == 'low' and 1 <= winning_number <= 18) or \
               (bet_value == 'high' and 19 <= winning_number <= 36):
                return bet_amount * 2
        
        return 0
    
    def _get_color(self, number):
        """Obtenir la couleur d'un numéro"""
        if number == 0:
            return 'green'
        elif number in self.red_numbers:
            return 'red'
        else:
            return 'black'

class PokerGame:
    def __init__(self):
        self.active_games = {}
    
    def start_game(self, user_id, bet_amount):
        """Commencer une partie de Poker (Jacks or Better)"""
        deck = self._create_deck()
        random.shuffle(deck)
        
        hand = [deck.pop() for _ in range(5)]
        
        game_state = {
            'game_id': f"poker_{user_id}_{datetime.now().timestamp()}",
            'user_id': user_id,
            'bet_amount': bet_amount,
            'deck': deck,
            'hand': hand,
            'held_cards': [False] * 5,
            'status': 'choosing',
            'created_at': datetime.now().isoformat()
        }
        
        self.active_games[game_state['game_id']] = game_state
        
        return {
            'success': True,
            'game_id': game_state['game_id'],
            'hand': hand,
            'status': 'choosing'
        }
    
    def hold_cards(self, game_id, held_positions):
        """Garder certaines cartes et en tirer de nouvelles"""
        if game_id not in self.active_games:
            return {'success': False, 'error': 'Partie non trouvée'}
        
        game = self.active_games[game_id]
        
        # Remplacer les cartes non gardées
        for i in range(5):
            if i not in held_positions:
                game['hand'][i] = game['deck'].pop()
        
        # Évaluer la main finale
        hand_rank, multiplier = self._evaluate_poker_hand(game['hand'])
        winnings = game['bet_amount'] * multiplier
        
        game['status'] = 'finished'
        game['hand_rank'] = hand_rank
        game['winnings'] = winnings
        
        return {
            'success': True,
            'final_hand': game['hand'],
            'hand_rank': hand_rank,
            'multiplier': multiplier,
            'winnings': winnings
        }
    
    def _create_deck(self):
        """Créer un jeu de 52 cartes"""
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [{'suit': suit, 'rank': rank, 'value': i + 2} for suit in suits for i, rank in enumerate(ranks)]
    
    def _evaluate_poker_hand(self, hand):
        """Évaluer une main de poker"""
        # TODO: Implémenter l'évaluation complète des mains de poker
        # Pour l'instant, retourner une main aléatoire
        hands = [
            ('Rien', 0),
            ('Paire de Valets+', 1),
            ('Double Paire', 2),
            ('Brelan', 3),
            ('Quinte', 4),
            ('Couleur', 6),
            ('Full', 9),
            ('Carré', 25),
            ('Quinte Flush', 50),
            ('Quinte Flush Royale', 800)
        ]
        return random.choice(hands)

class SlotMachine:
    def __init__(self):
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '7️⃣']
        self.payouts = {
            '🍒🍒🍒': 10,
            '🍋🍋🍋': 20,
            '🍊🍊🍊': 30,
            '🍇🍇🍇': 40,
            '⭐⭐⭐': 100,
            '💎💎💎': 500,
            '7️⃣7️⃣7️⃣': 1000
        }
    
    def spin(self, bet_amount):
        """Faire tourner la machine à sous"""
        reels = [random.choice(self.symbols) for _ in range(3)]
        combination = ''.join(reels)
        
        multiplier = self.payouts.get(combination, 0)
        winnings = bet_amount * multiplier
        
        return {
            'success': True,
            'reels': reels,
            'combination': combination,
            'multiplier': multiplier,
            'winnings': winnings,
            'jackpot': combination == '7️⃣7️⃣7️⃣'
        }
