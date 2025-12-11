# Contenido para: poker_engine/data_models.py

import random
from enum import Enum


# --- 1. Definiciones Básicas de Cartas ---

class Suit(Enum): # Palo
    HEARTS = "Corazones"
    DIAMONDS = "Diamantes"
    CLUBS = "Tréboles"
    SPADES = "Picas"


class Rank(Enum): # Valor
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
        self.name = name # Nombre del jugador
        self.stack = stack # Fichas que posee el jugador
        self.hand = []  # Sus 2 cartas privadas
        self.current_bet = 0
        self.is_active = True # Participación en la ronda
        self.is_all_in = False
        self.has_called = False #Ha realziado al menos una accion en la ronda (puede ser call/pass)
        self.evaluation = None #Evaluación de sus cartas
        self.is_evaluated = False #Ha sido valorado, comparado y revisado si le corresponde sidepot

    def clear_hand(self):
        self.hand = []
        self.current_bet = 0
        self.evaluation = None
        if self.stack > 0:
            self.is_active = True
        else:
            self.is_active = False

    def change_round(self):
        self.has_called = False

    def action(self, current_raise_to_match):
        pass

class HumanPlayer(Player):
    def action(self, current_raise_to_match):
        amount_raised = 0
        if not self.is_all_in:
            opcion = input("Please, choose an option from the provided list, using its assigned number. Choose Action: ")
            opcion = int(opcion)

            while opcion < 1 or opcion > 4:
                opcion = input("Please, choose an option from the provided list, using its assigned number. Choose Action: ")
                opcion = int(opcion)
                
            if opcion == 1:
                if self.current_bet < current_raise_to_match:
                    if self.stack > current_raise_to_match:
                        amount_raised = current_raise_to_match - self.current_bet
                        self.current_bet = current_raise_to_match
                    else:
                        self.current_bet = self.stack
                        self.is_all_in = True
            elif opcion == 2:
                amount_raised = int(input("Choose Amount to Raise: "))
                if amount_raised >= self.stack:
                    amount_raised = input("Invalid Raise. Choose Amount to Raise: ")

                current_raise_to_match += amount_raised
                amount_raised = current_raise_to_match
                self.current_bet = current_raise_to_match

            elif opcion == 3:
                self.is_active = False
                self.stack -= self.current_bet
                self.current_bet = 0
                amount_raised = 0

            elif opcion == 4:
                self.current_bet = self.stack
                self.is_all_in = True
                
                if self.current_bet > current_raise_to_match:
                    amount_raised = self.current_bet - current_raise_to_match
                    current_raise_to_match = self.current_bet
        
        self.has_called = True
        self.stack -= amount_raised
        return current_raise_to_match, amount_raised


# --- 4. El Estado del Juego ---

#Ronda actual en la que se encuentra
class Round(Enum):
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3
    ShowHand = 4
    EndGame = 5


class GameState:
    def __init__(self, players: list[Player], baseblind: int):
        self.players = players # Lista de jugadores de la partida
        self.pot = 0 # Bote
        self.community_cards = []
        self.burned_cards = []
        self.deck = Deck() # Mazo para robar
        self.turn_to_act_index = 0 # De quién es el turno
        self.small_blind_indx = 0 # Jugador que da la ciega pequeña de la mano (se le considera que empieza jugando aunque sea accion forzada)
        self.current_raise_to_match = 0 # Nivel de la apuesta a igualar
        self.last_raiser = 0 # Ultimo jugador en subir la apuesta
        self.round = Round.PreFlop

        #Definir las ciegas minimas como parte de la partida permitira subirlas entre manos 
        #(garantizando que eventualmente haya un ganador en torneos eliminatorios)
        self.smallBlind = baseblind #Ciega pequeña minima
        self.bigBlind = baseblind * 2 #Ciega grande minima

        #Jugadores ganadores y cantidad (Para su uso en visualizacion)
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
        self.community_cards = []
        self.deck = Deck()
        self.small_blind_indx   = (self.small_blind_indx + 1) % len(self.players)
        self.turn_to_act_index = self.small_blind_indx

        for player in self.players:
            player.clear_hand()

        self.winner_players = []
        self.amount_won = []