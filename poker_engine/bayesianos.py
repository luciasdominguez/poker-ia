import random
from poker_engine.poker_rules import HandEvaluator


def prepare_fuzzy_inputs(player, game_state):
    """Calcula las variables numéricas que el controlador Fuzzy necesita."""
    # 1. Probabilidad Bayesiana (Inferencia)
    win_prob = estimate_equity(player.hand, game_state)  # Función ya definida

    # 2. Pot Odds: ¿Es caro o barato ir?
    amount_to_call = game_state.current_raise_to_match - player.current_bet
    total_pot = game_state.pot + amount_to_call
    pot_odds = amount_to_call / total_pot if total_pot > 0 else 0

    # 3. Stack relativo (ej: relación stack / ciega grande)
    relative_stack = min(player.stack / (game_state.bigBlind * 20), 1.0)

    return win_prob, pot_odds, relative_stack


def estimate_equity(player_hand, game_state, iterations=500):
    evaluator = HandEvaluator()
    wins = 0
    community = game_state.community_cards
    opponents_count = game_state.number_of_active() - 1

    if opponents_count <= 0: return 1.0

    # Filtrar mazo
    known_cards = player_hand + community
    # Usamos los modelos de datos que ya tienes para reconstruir el mazo
    from poker_engine.data_models import Card, Suit, Rank
    full_deck = [Card(r, s) for s in Suit for r in Rank]
    remaining_deck = [c for c in full_deck if not any(
        c.rank == k.rank and c.suit == k.suit for k in known_cards)]

    for _ in range(iterations):
        temp_deck = remaining_deck[:]
        random.shuffle(temp_deck)

        opp_hands = [[temp_deck.pop(), temp_deck.pop()] for _ in range(opponents_count)]
        sim_community = community[:]
        while len(sim_community) < 5:
            sim_community.append(temp_deck.pop())

        my_score = evaluator.evaluate_hand(player_hand, sim_community)
        if all(my_score > evaluator.evaluate_hand(oh, sim_community) for oh in opp_hands):
            wins += 1

    return wins / iterations