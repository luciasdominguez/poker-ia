# Contenido para: poker_engine/data_models.py

import random
from enum import Enum


# --- 1. Definiciones Básicas de Cartas ---

class Suit(Enum):
    HEARTS = "Corazones"
    DIAMONDS = "Diamantes"
    CLUBS = "Tréboles"
    SPADES = "Picas"


class Rank(Enum):
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
        self.name = name
        self.stack = stack
        self.hand = []  # Sus 2 cartas privadas
        self.current_bet = 0
        self.is_active = True
        self.is_all_in = False

    def clear_hand(self):
        self.hand = []
        self.current_bet = 0


# --- 4. El Estado del Juego ---

class GameState:
    def __init__(self, players: list[Player]):
        self.players = players
        self.pot = 0
        self.community_cards = []
        self.deck = Deck()
        self.turn_to_act_index = 0
        self.current_raise_to_match = 0

    def reset_for_new_hand(self):
        self.pot = 0
        self.community_cards = []
        self.deck = Deck()