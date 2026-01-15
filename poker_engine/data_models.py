# Contenido para: poker_engine/data_models.py
import random
from enum import Enum
# --- 1. Definiciones Básicas de Cartas ---
class Suit(Enum):  # Palo
    HEARTS = "Corazones"
    DIAMONDS = "Diamantes"
    CLUBS = "Tréboles"
    SPADES = "Picas"


class Rank(Enum):  # Valor
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"Card({self.rank.name}, {self.suit.name})"

    def __str__(self):
        return f"{self.rank.name} de {self.suit.value}"


# --- 2. El Mazo ---

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> Card:
        if not self.cards:
            raise ValueError("Mazo vacío")
        return self.cards.pop()


# --- 3. El Jugador ---

class Player:
    def __init__(self, name: str, stack: int):
        self.name = name  # Nombre del jugador
        self.stack = stack  # Fichas que posee el jugador
        self.hand = []  # Sus 2 cartas privadas
        self.current_bet = 0
        self.total_bet_in_hand = 0 # Fichas apostadas en total en esta mano (acumulado)
        self.is_active = True  # Participación en la ronda
        self.is_all_in = False
        self.has_called = False  # Ha realziado al menos una accion en la ronda (puede ser call/pass)
        self.evaluation = None  # Evaluación de sus cartas
        self.is_evaluated = False  # Ha sido valorado, comparado y revisado si le corresponde sidepot

    def clear_hand(self):
        self.hand = []
        self.current_bet = 0
        self.total_bet_in_hand = 0
        self.evaluation = None
        if self.stack > 0:
            self.is_active = True
        else:
            self.is_active = False

    def change_round(self):
        self.has_called = False

    def action(self, current_raise_to_match):
        pass


class AIPlayer(Player):
    def __init__(self, name: str, stack: int, game_reference, difficulty='hard'):
        super().__init__(name, stack)
        self.game = game_reference
        self.difficulty = difficulty

    def action(self, current_raise_to_match):
        from poker_engine.bayesianos import estimate_equity
        from poker_engine.Logica_fuzzy import get_fuzzy_decision  # Importación de la lógica de tu compañero

        if not self.is_active or self.is_all_in:
            self.has_called = True
            return current_raise_to_match, 0

        # --- PARTE A: Preparación de Inputs (Tú) ---

        # 1. Probabilidad de victoria (Bayesiana)
        win_prob = estimate_equity(self.hand, self.game)

        # 2. Pot Odds: ¿Cuánto me cuesta el bote actual?
        amount_to_call = current_raise_to_match - self.current_bet
        total_pot = self.game.pot + amount_to_call
        # Si el bote es 0 (raro), las odds son 0
        pot_odds = amount_to_call / total_pot if total_pot > 0 else 0

        # 3. Stack Relativo: ¿Tengo muchas o pocas fichas? (Normalizado 0-1)
        # Tomamos como referencia 20 ciegas grandes para decir que un stack es "grande" (1.0)
        rel_stack = min(self.stack / (self.game.bigBlind * 20), 1.0)

        # --- PARTE B: Inferencia Borrosa (Tu compañero) ---

        # La función devuelve:
        # fuzzy_action: 1 (Call/Pass), 2 (Raise), 3 (Fold)
        # bet_multiplier: % del stack a apostar si es Raise (0.0 a 1.0)
        fuzzy_action, bet_multiplier = get_fuzzy_decision(win_prob, pot_odds, rel_stack, self.difficulty)

        # --- PARTE C: Ejecución en el motor ---

        # --- PARTE C: Ejecución corregida ---
        if fuzzy_action == 3:  # Fold
            self.is_active = False
            self.has_called = True
            print(f"> {self.name} se retira (Fold).")
            return current_raise_to_match, 0

        # CAP DE SUBIDAS: Si ya hubo 4 o más subidas en esta ronda, forzamos Call
        if fuzzy_action == 2:  # Raise
             if self.game.raises_this_round >= 4:
                 fuzzy_action = 1 # Force Call

        if fuzzy_action == 2:  # Raise
            extra_raise = int(self.stack * bet_multiplier)
            new_total = current_raise_to_match + extra_raise
            
            # Ajuste minimo de subida (minraise)
            min_raise = self.game.bigBlind 
            if extra_raise < min_raise and (self.stack > current_raise_to_match - self.current_bet + min_raise):
                 extra_raise = min_raise
                 new_total = current_raise_to_match + extra_raise
            
        else:  # Call / Pass
            new_total = current_raise_to_match

        actual_pay = new_total - self.current_bet

        # Validación de fondos
        option_str = "paga"
        if fuzzy_action == 2: option_str = "sube"
        
        if actual_pay >= self.stack:
            actual_pay = self.stack
            new_total = self.current_bet + self.stack
            self.is_all_in = True
            option_str = "va All-in"

        self.stack -= actual_pay  # RESTA real del stack
        self.current_bet = new_total
        self.has_called = True
        
        if fuzzy_action == 2 and not self.is_all_in:
             print(f"> {self.name} sube a {new_total} (Apostó {actual_pay}).")
        elif self.is_all_in:
             print(f"> {self.name} {option_str} por {actual_pay}!")
        elif actual_pay > 0:
             print(f"> {self.name} paga {actual_pay}.")
        else:
             print(f"> {self.name} pasa (Check).")

        return new_total, actual_pay


class HumanPlayer(Player):
    def action(self, current_raise_to_match):
        amount_to_pay = 0  # Lo que realmente sacamos del bolsillo en esta acción

        if not self.is_all_in:
            # Mostramos al usuario cuánto debe poner para igualar
            needed_to_call = current_raise_to_match - self.current_bet
            if needed_to_call > 0:
                print(f"Para igualar: {needed_to_call}")
            else:
                print("Puedes pasar (coste 0).")

            opcion = int(input("1-Igualar/Pasar, 2-Subir, 3-Retirarse, 4-All-in: "))

            if opcion == 1:  # Call / Check
                amount_to_pay = min(needed_to_call, self.stack)
                self.current_bet += amount_to_pay
                if self.stack <= amount_to_pay: self.is_all_in = True

            elif opcion == 2:  # Raise
                min_r = self.game.bigBlind
                print(f"Minima subida permitida: {min_r}")
                raise_amount = int(input("¿Cuánto MÁS de la apuesta actual quieres subir?: "))
                
                # Validation loop
                needed_to_call = current_raise_to_match - self.current_bet
                max_raise = self.stack - needed_to_call
                
                while raise_amount < min_r and raise_amount < max_raise:
                     print(f"La subida debe ser al menos {min_r} (o All-In).")
                     raise_amount = int(input("¿Cuánto MÁS de la apuesta actual quieres subir?: "))

                total_new_bet = current_raise_to_match + raise_amount
                amount_to_pay = total_new_bet - self.current_bet

                if amount_to_pay >= self.stack:  # Si no le alcanza, es un All-in
                    amount_to_pay = self.stack
                    self.is_all_in = True
                
                self.current_bet += amount_to_pay
                current_raise_to_match = self.current_bet

            elif opcion == 3:  # Fold
                self.is_active = False
                return current_raise_to_match, 0

            elif opcion == 4:  # All-in
                amount_to_pay = self.stack
                self.current_bet += amount_to_pay
                self.is_all_in = True
                if self.current_bet > current_raise_to_match:
                    current_raise_to_match = self.current_bet

        self.stack -= amount_to_pay
        self.has_called = True
        return current_raise_to_match, amount_to_pay


# --- 4. El Estado del Juego ---

# Ronda actual en la que se encuentra
class Round(Enum):
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3
    ShowHand = 4
    EndGame = 5



class SidePot:
    def __init__(self, amount: int, eligible_players: list[str]):
        self.amount = amount
        self.eligible_players = eligible_players

    def __repr__(self):
        return f"SidePot({self.amount}, {self.eligible_players})"

class GameState:
    def __init__(self, players: list[Player], baseblind: int):
        self.players = players  # Lista de jugadores de la partida
        self.pot = 0  # Bote acumulado para display. Bote real se calcula en side_pots
        self.side_pots = [] # Lista de SidePot
        self.community_cards = []

        self.burned_cards = []
        self.deck = Deck()  # Mazo para robar
        self.turn_to_act_index = 0  # De quién es el turno
        self.small_blind_indx = 0  # Jugador que da la ciega pequeña de la mano (se le considera que empieza jugando aunque sea accion forzada)
        self.current_raise_to_match = 0  # Nivel de la apuesta a igualar
        self.last_raiser = 0  # Ultimo jugador en subir la apuesta
        self.raises_this_round = 0 # Contador de subidas en la ronda actual
        self.round = Round.PreFlop

        # Definir las ciegas minimas como parte de la partida permitira subirlas entre manos
        # (garantizando que eventualmente haya un ganador en torneos eliminatorios)
        self.smallBlind = baseblind  # Ciega pequeña minima
        self.bigBlind = baseblind * 2  # Ciega grande minima

        # Jugadores ganadores y cantidad (Para su uso en visualizacion)
        self.winner_players = []
        self.amount_won = []

    def number_of_active(self):
        count = 0
        for player in self.players:
            if player.is_active == True:
                count += 1
        return count

    def minimum_bet_player(self):
        player_index = None
        player_bet = None

        for index, player in enumerate(self.players):
            if player.is_active == True:
                if player_bet == None or player.current_bet < player_bet:
                    player_bet = player.current_bet
                    player_index = index
        return player_index, player_bet

    def any_active(self):
        for player in self.players:
            if player.is_active:
                return True
        return False

    def yet_to_evaluate(self):
        for player in self.players:
            if not player.is_evaluated:
                return True
        return False

    def reset_for_new_hand(self):
        self.pot = 0
        self.side_pots = []
        self.community_cards = []
        self.deck = Deck()
        self.small_blind_indx = (self.small_blind_indx + 1) % len(self.players)
        self.turn_to_act_index = self.small_blind_indx

        for player in self.players:
            player.clear_hand()

        self.winner_players = []
        self.amount_won = []