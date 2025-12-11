from data_models import Rank,Card
from enum import Enum
from collections import Counter
from typing import List, Tuple, Optional


class HandRank(Enum):
    """Define los 9 rangos posibles de manos de póker, de más fuerte a más débil."""
    ROYAL_FLUSH = 10  # Escalera real: 10, J, Q, K, A del mismo palo
    STRAIGHT_FLUSH = 9  # Escalera de color
    FOUR_OF_A_KIND = 8  # Póker
    FULL_HOUSE = 7  # Full
    FLUSH = 6  # Color
    STRAIGHT = 5  # Escalera
    THREE_OF_A_KIND = 4  # Trío
    TWO_PAIR = 3  # Doble Pareja
    ONE_PAIR = 2  # Pareja
    HIGH_CARD = 1  # Carta Alta


class HandEvaluation:
    """Almacena el rango de la mano y los 'kickers' (desempates) para comparación."""

    def __init__(self, rank: HandRank, kickers: Tuple[int, ...]):
        self.rank = rank
        # Kickers: tupla de valores numéricos de las cartas, ordenados por importancia.
        self.kickers = kickers

    def __lt__(self, other):
        """Permite comparar dos evaluaciones de mano (para determinar el ganador)."""
        # 1. Compara el rango (el valor del Enum)
        if self.rank.value != other.rank.value:
            return self.rank.value < other.rank.value
        # 2. Si los rangos son iguales, compara los kickers
        return self.kickers < other.kickers

    def __repr__(self):
        return f"HandEvaluation(Rank={self.rank.name}, Kickers={self.kickers})"

    def __str__(self):
        return f"{self.rank.value}. {self.rank.name} (Desempates: {self.kickers})"


# --- 6. El Evaluador de Manos (Hand Evaluator) ---

class HandEvaluator:
    """Clase responsable de determinar el mejor rango de mano de 5 cartas de 7."""
    RANK_VALUES = {rank: rank.value for rank in Rank}

    def _get_rank_values(self, cards: List[Card]) -> List[int]:
        """Retorna los valores numéricos de las cartas, ordenados de mayor a menor."""
        return sorted([self.RANK_VALUES[card.rank] for card in cards], reverse=True)

    def _get_counts(self, cards: List[Card]):
        """Obtiene el conteo de rangos y el conteo de palos."""
        rank_values = self._get_rank_values(cards)
        rank_counts = Counter(rank_values)
        suit_counts = Counter([card.suit for card in cards])
        return rank_counts, suit_counts

    def _check_straight_logic(self, ranks: List[int]) -> Tuple[bool, int]:
        """Lógica subyacente para detectar escaleras y devolver la carta alta."""
        unique_ranks = sorted(list(set(ranks)), reverse=True)

        # Caso especial: A-2-3-4-5 (As bajo, se puntúa con 5)
        if 14 in unique_ranks and 5 in unique_ranks and 4 in unique_ranks and 3 in unique_ranks and 2 in unique_ranks:
            return True, 5

        # Búsqueda de secuencias de 5
        for i in range(len(unique_ranks) - 4):
            # Si el valor actual es 4 más grande que el valor en la posición i+4, es una escalera.
            if unique_ranks[i] == unique_ranks[i + 4] + 4:
                return True, unique_ranks[i]

        return False, 0

    def _find_best_five_card_flush(self, cards: List[Card]) -> Optional[List[Card]]:
        """Busca y retorna las 5 cartas más altas que forman un color."""
        _, suit_counts = self._get_counts(cards)

        flush_suit = next((suit for suit, count in suit_counts.items() if count >= 5), None)

        if not flush_suit:#color
            return None

        # Filtra las cartas del palo del color, y toma las 5 más altas.
        flush_cards = [card for card in cards if card.suit == flush_suit]
        flush_cards.sort(key=lambda c: self.RANK_VALUES[c.rank], reverse=True)

        return flush_cards[:5]

    # --- Métodos de Evaluación de Rangos (De más fuerte a más débil) ---

    def _check_straight_flush(self, all_cards: List[Card]) -> Optional[HandEvaluation]:
        """1. Escalera de Color (incluye Escalera Real)"""
        best_flush_cards = self._find_best_five_card_flush(all_cards)

        if not best_flush_cards:
            return None

        flush_ranks = self._get_rank_values(best_flush_cards)
        is_straight, high_card_rank = self._check_straight_logic(flush_ranks)

        if is_straight:
            # Royal Flush (Escalera Real) A-K-Q-J-10 del mismo palo
            if high_card_rank == 14:
                return HandEvaluation(HandRank.ROYAL_FLUSH, (14,))

                # Straight Flush (A-2-3-4-5) - se puntúa con 5 para desempate
            if high_card_rank == 5 and 14 in flush_ranks:
                return HandEvaluation(HandRank.STRAIGHT_FLUSH, (5,))

            # Straight Flush Estándar
            return HandEvaluation(HandRank.STRAIGHT_FLUSH, (high_card_rank,))

        return None

    def _check_four_of_a_kind(self, rank_counts: Counter) -> Optional[HandEvaluation]:
        """2. Póker (Cuatro del Mismo Valor)"""
        four_rank = next((rank for rank, count in rank_counts.items() if count >= 4), None)

        if four_rank:
            # Kicker: la carta restante más alta
            other_ranks = sorted([rank for rank in rank_counts.keys() if rank != four_rank], reverse=True)
            kicker = other_ranks[
                0] if other_ranks else four_rank  # En caso de 5 cartas de Póker (no posible en Hold'em)
            return HandEvaluation(HandRank.FOUR_OF_A_KIND, (four_rank, kicker))
        return None

    def _check_full_house(self, rank_counts: Counter) -> Optional[HandEvaluation]:
        """3. Full (Trío + Pareja)"""

        # Encontrar el trío más alto
        three_ranks = sorted([rank for rank, count in rank_counts.items() if count >= 3], reverse=True)
        if not three_ranks: return None

        three_rank = three_ranks[0]

        # Encontrar la mejor pareja (o segundo trío) que no sea el trío principal
        pair_rank = None

        # Primero, busca tríos más bajos (ej. 999 888 -> 999 88)
        if len(three_ranks) >= 2:
            pair_rank = three_ranks[1]
        else:
            # Si no hay segundo trío, busca la pareja más alta
            pair_ranks = sorted([rank for rank, count in rank_counts.items() if count >= 2 and rank != three_rank],
                                reverse=True)
            if pair_ranks:
                pair_rank = pair_ranks[0]

        if three_rank and pair_rank:
            # Kickers: (rango del trío, rango de la pareja)
            return HandEvaluation(HandRank.FULL_HOUSE, (three_rank, pair_rank))

        return None

    def _check_flush(self, all_cards: List[Card]) -> Optional[HandEvaluation]:
        """4. Color (Cinco cartas del mismo palo)"""
        best_flush_cards = self._find_best_five_card_flush(all_cards)

        if best_flush_cards:
            # Kickers son los 5 valores de las cartas del color, de mayor a menor.
            kickers = tuple(self._get_rank_values(best_flush_cards))
            return HandEvaluation(HandRank.FLUSH, kickers)
        return None

    def _check_straight(self, all_cards: List[Card]) -> Optional[HandEvaluation]:
        """5. Escalera (Cinco cartas en secuencia)"""
        ranks = self._get_rank_values(all_cards)
        is_straight, high_card_rank = self._check_straight_logic(ranks)

        if is_straight:
            # Kicker para la escalera es solo la carta alta.
            # (El as bajo (5) o la carta alta de la secuencia)
            return HandEvaluation(HandRank.STRAIGHT, (high_card_rank,))

        return None

    def _check_n_of_a_kind_and_pairs(self, rank_counts: Counter, all_cards: List[Card]) -> Optional[HandEvaluation]:
        """6, 7 y 8. Trío, Doble Pareja y Pareja."""

        # Encontrar agrupaciones (Tríos y Parejas)
        three_ranks = sorted([rank for rank, count in rank_counts.items() if count >= 3], reverse=True)
        pair_ranks = sorted([rank for rank, count in rank_counts.items() if count >= 2], reverse=True)

        # Obtener todos los rangos (valores) únicos para los kickers
        all_unique_ranks = sorted(rank_counts.keys(), reverse=True)

        # 6. Trío (Three of a Kind)
        if three_ranks:
            three_rank = three_ranks[0]

            # Kickers: las 2 cartas más altas que no forman parte del trío
            other_ranks = [rank for rank in all_unique_ranks if rank != three_rank]
            kickers = tuple([three_rank] + other_ranks[:2])
            return HandEvaluation(HandRank.THREE_OF_A_KIND, kickers)

        # 7. Doble Pareja (Two Pair)
        if len(pair_ranks) >= 2:
            high_pair = pair_ranks[0]
            low_pair = pair_ranks[1]

            # Kicker: la carta más alta que no forma parte de ninguna de las parejas
            other_ranks = [rank for rank in all_unique_ranks if rank != high_pair and rank != low_pair]
            kicker = other_ranks[0] if other_ranks else 0

            # Kickers: (Pareja Alta, Pareja Baja, Kicker)
            kickers = tuple([high_pair, low_pair, kicker])
            return HandEvaluation(HandRank.TWO_PAIR, kickers)

        # 8. Pareja (One Pair)
        if len(pair_ranks) >= 1:
            pair_rank = pair_ranks[0]

            # Kickers: las 3 cartas más altas que no forman parte de la pareja
            other_ranks = [rank for rank in all_unique_ranks if rank != pair_rank]
            kickers = tuple([pair_rank] + other_ranks[:3])
            return HandEvaluation(HandRank.ONE_PAIR, kickers)

        return None

    def _check_high_card(self, all_cards: List[Card]) -> HandEvaluation:
        """9. Carta Alta (ningún otro rango)"""
        # Kickers son las 5 cartas más altas disponibles.
        kickers = tuple(self._get_rank_values(all_cards)[:5])
        return HandEvaluation(HandRank.HIGH_CARD, kickers)

    def evaluate_hand(self, player_hand: List[Card], community_cards: List[Card]) -> HandEvaluation:
        """
        Método principal para evaluar la mejor mano de 5 cartas de las 7 disponibles.
        """
        all_cards = player_hand + community_cards

        # Manejar el caso de que aún no haya suficientes cartas (ej. antes del River)
        if len(all_cards) < 5:
            return self._check_high_card(all_cards)

            # 1. Preparación para chequeos basados en Rangos
        rank_counts, _ = self._get_counts(all_cards)

        # 2. Chequeos en orden descendente de fuerza

        # A. Straight Flush (incluye Royal Flush)
        evaluation = self._check_straight_flush(all_cards)
        if evaluation: return evaluation

        # B. Four of a Kind (Póker)
        evaluation = self._check_four_of_a_kind(rank_counts)
        if evaluation: return evaluation

        # C. Full House (Full)
        evaluation = self._check_full_house(rank_counts)
        if evaluation: return evaluation

        # D. Flush (Color)
        evaluation = self._check_flush(all_cards)
        if evaluation: return evaluation

        # E. Straight (Escalera)
        evaluation = self._check_straight(all_cards)
        if evaluation: return evaluation

        # F. Three of a Kind, Two Pair, and One Pair
        # Full House, Flush, and Straight have been checked. Now check for three of a kind, two pair and one pair.
        evaluation = self._check_n_of_a_kind_and_pairs(rank_counts, all_cards)
        if evaluation: return evaluation

        # I. High Card (Carta Alta)

        return self._check_high_card(all_cards)
