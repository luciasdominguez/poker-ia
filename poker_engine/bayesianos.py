import random
import copy
import poker_engine.data_models as dm
from poker_engine.poker_rules import HandEvaluator


class AIPlayer(dm.Player):
    def __init__(self, name: str, stack: int, game_reference: dm.GameState):
        super().__init__(name, stack)
        self.game = game_reference  # Ya tenemos acceso al estado global
        self.evaluator = HandEvaluator()  # Reutilizamos tu evaluador

    def estimate_equity(self, iterations=500):
        """
        Método Bayesiano: Simulación de Monte Carlo para estimar la
        probabilidad de ganar (Equity) basada en la evidencia actual.
        """
        wins = 0
        # 1. Obtener evidencia del GameState
        community = self.game.community_cards
        opponents_count = self.game.number_of_active() - 1

        if opponents_count <= 0: return 1.0

        # 2. Crear mazo excluyendo cartas conocidas (mano propia + mesa)
        known_cards = self.hand + community
        full_deck = [dm.Card(r, s) for s in dm.Suit for r in dm.Rank]
        remaining_deck = [c for c in full_deck if not any(
            c.rank == k.rank and c.suit == k.suit for k in known_cards)]

        # 3. Simular escenarios posibles (Posterior)
        for _ in range(iterations):
            temp_deck = remaining_deck[:]
            random.shuffle(temp_deck)

            # Repartir a oponentes
            opp_hands = [[temp_deck.pop(), temp_deck.pop()] for _ in range(opponents_count)]

            # Completar la mesa (Flop, Turn o River)
            sim_community = community[:]
            while len(sim_community) < 5:
                sim_community.append(temp_deck.pop())

            # Evaluar usando tu HandEvaluator
            my_score = self.evaluator.evaluate_hand(self.hand, sim_community)

            is_winner = True
            for oh in opp_hands:
                if self.evaluator.evaluate_hand(oh, sim_community) > my_score:
                    is_winner = False
                    break

            if is_winner: wins += 1

        return wins / iterations

    def action(self, current_raise_to_match):
        """
        Implementación de la acción usando el cálculo bayesiano.
        """
        if not self.is_active or self.is_all_in:
            self.has_called = True
            return current_raise_to_match, 0

        # Ejecutar estimación
        win_prob = self.estimate_equity()

        # Lógica de decisión simplificada (A la espera de la Lógica Borrosa)
        # Aquí la IA decide basándose en la probabilidad calculada
        amount_to_call = current_raise_to_match - self.current_bet

        if win_prob > 0.7:  # Mano muy fuerte
            # Subir apuesta
            raise_amount = int(self.stack * 0.2)
            new_total = current_raise_to_match + raise_amount
            actual_raise = new_total - self.current_bet

            if actual_raise >= self.stack:  # All-in
                actual_raise = self.stack
                self.current_bet += self.stack
                self.is_all_in = True
                self.stack = 0
                self.has_called = True
                return self.current_bet, actual_raise

            self.current_bet = new_total
            self.stack -= actual_raise
            self.has_called = True
            return new_total, actual_raise

        elif win_prob > 0.3 or amount_to_call == 0:  # Mano decente o gratis
            # Hacer Call
            if amount_to_call >= self.stack:
                actual_pay = self.stack
                self.current_bet += self.stack
                self.is_all_in = True
                self.stack = 0
            else:
                actual_pay = amount_to_call
                self.current_bet = current_raise_to_match
                self.stack -= actual_pay

            self.has_called = True
            return current_raise_to_match, actual_pay

        else:  # Mano débil
            # Fold
            self.is_active = False
            self.has_called = True
            return current_raise_to_match, 0