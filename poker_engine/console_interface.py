import os
import poker_engine.data_models as dm
from enum import Enum


# Contiene las funciones para pintar la mesa (interfaz por consola con el usuario)
class Table:
    def __init__(self, game: dm.GameState):
        self.game = game

    def limpiar_consola(self):
        print("\033c", end="")

    def interfaz_basica(self):
        match self.game.round:
            case dm.Round.PreFlop:
                self.limpiar_consola()
                actual_player = self.game.players[self.game.turn_to_act_index]
                if isinstance(actual_player, dm.HumanPlayer):

                    # Caracteristicas globales de la partida:
                    print(" ===== Estado de la Mesa ===== ")
                    print(" Ronda: Pre-Flop ")
                    print(f" Bote Principal: {self.game.pot}")
                    print(f" Cartas Comunitarias: {self.game.community_cards}")
                    print(" ========================")

                # Características del propio jugador:
                print(f" ===== Jugador {self.game.turn_to_act_index + 1} ===== ")
                print(" ========================")
                print(f" Fichas: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Apuesta: {self.game.players[self.game.turn_to_act_index].current_bet}")
                to_call = self.game.current_raise_to_match - actual_player.current_bet
                if isinstance(actual_player, dm.HumanPlayer):
                    print(f" Cartas: {actual_player.hand}")
                    print(" ========================")
                    if to_call > 0:
                        print(f" -> Tienes que pagar: {to_call}")
                    else:
                        print(" -> Puedes pasar")

                    print(" ========================")
                    # Acciones a realizar
                    print(f" ===== Acciones Posibles ===== ")
                    print(" ========================")
                    print("1- Igualar/Pasar")
                    print("2 - Subir")
                    print("3 - Retirarse")
                    print("4 - All in")
                    print(" ========================")
            case dm.Round.Flop:
                self.limpiar_consola()
                actual_player = self.game.players[self.game.turn_to_act_index]
                if isinstance(actual_player, dm.HumanPlayer):
                    # Caracteristicas globales de la partida:
                    print(" ===== Estado de la Mesa ===== ")
                    print(" Ronda: Flop ")
                    print(f" Bote Principal: {self.game.pot}")
                    print(f" Cartas Comunitarias: {self.game.community_cards}")
                    print(" ========================")

                # Características del propio jugador:
                print(f" ===== Jugador {self.game.turn_to_act_index + 1} ===== ")
                print(" ========================")
                print(f" Fichas: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Apuesta: {self.game.players[self.game.turn_to_act_index].current_bet}")
                actual_player = self.game.players[self.game.turn_to_act_index]

                if isinstance(actual_player, dm.HumanPlayer):
                    print(f" Cartas: {actual_player.hand}")
                    print(" ========================")
                    to_call = self.game.current_raise_to_match - actual_player.current_bet

                    if to_call > 0:
                        print(f" -> Tienes que pagar: {to_call}")
                    else:
                        print(" -> Puedes pasar")
                    # Acciones a realizar
                    print(f" ===== Acciones Posibles ===== ")
                    print(" ========================")
                    print("1- Igualar/Pasar")
                    print("2 - Subir")
                    print("3 - Retirarse")
                    print("4 - All in")
                    print(" ========================")

            case dm.Round.Turn:
                self.limpiar_consola()
                actual_player = self.game.players[self.game.turn_to_act_index]
                if isinstance(actual_player, dm.HumanPlayer):
                    # Caracteristicas globales de la partida:
                    print(" ===== Estado de la Mesa ===== ")
                    print(" Ronda: Turn ")
                    print(f" Bote Principal: {self.game.pot}")
                    print(f" Cartas Comunitarias: {self.game.community_cards}")
                    print(" ========================")
                # Características del propio jugador:
                print(f" ===== Jugador {self.game.turn_to_act_index + 1} ===== ")
                print(" ========================")
                print(f" Fichas: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Apuesta: {self.game.players[self.game.turn_to_act_index].current_bet}")

                if isinstance(actual_player, dm.HumanPlayer):
                    print(f" Cartas: {actual_player.hand}")
                    print(" ========================")
                    to_call = self.game.current_raise_to_match - actual_player.current_bet

                    if to_call > 0:
                        print(f" -> Tienes que pagar: {to_call}")
                    else:
                        print(" -> Puedes pasar")
                    # Acciones a realizar
                    print(f" ===== Acciones Posibles ===== ")
                    print(" ========================")
                    print("1- Igualar/Pasar")
                    print("2 - Subir")
                    print("3 - Retirarse")
                    print("4 - All in")
                    print(" ========================")

            case dm.Round.River:
                actual_player = self.game.players[self.game.turn_to_act_index]
                if isinstance(actual_player, dm.HumanPlayer):
                    # Caracteristicas globales de la partida:
                    print(" ===== Estado de la Mesa ===== ")
                    print(" Ronda: River ")
                    print(f" Bote Principal: {self.game.pot}")
                    print(f" Cartas Comunitarias: {self.game.community_cards}")
                    print(" ========================")
                # Características del propio jugador:
                print(f" ===== Jugador {self.game.turn_to_act_index + 1} ===== ")
                print(" ========================")
                print(f" Fichas: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Apuesta: {self.game.players[self.game.turn_to_act_index].current_bet}")
                if isinstance(actual_player, dm.HumanPlayer):
                    print(f" Cartas: {actual_player.hand}")
                    print(" ========================")
                    to_call = self.game.current_raise_to_match - actual_player.current_bet

                    if to_call > 0:
                        print(f" -> Tienes que pagar: {to_call}")
                    else:
                        print(" -> Puedes pasar")
                    # Acciones a realizar
                    print(f" ===== Acciones Posibles ===== ")
                    print(" ========================")
                    print("1- Igualar/Pasar")
                    print("2 - Subir")
                    print("3 - Retirarse")
                    print("4 - All in")
                    print(" ========================")

            case dm.Round.ShowHand:
                self.limpiar_consola()
                # Caracteristicas globales de la partida:
                print(" ===== Estado de la Mesa ===== ")
                print(" Ronda: Mostrando Cartas (Showdown) ")
                print(f" Bote Principal: {self.game.pot}")
                print(f" Cartas Comunitarias: {self.game.community_cards}")
                print(" ========================")

                # Manos de cada jugador
                print(" ===== Cartas de Jugadores ===== ")
                print(" ========================")
                for player in self.game.players:
                    if player.is_active == True:
                        print(f"Jugador {player.name}: {player.hand}")

                # Mostrar ganadores y cantidad:
                print(" ===== Ganadores =====")
                print(" ========================")
                print(f"Jugadores: {self.game.winner_players}")
                print(f"Cantidad ganada: {self.game.amount_won}")
                print(" ========================")

                # Acciones a realizar
                print(f" ===== Acciones Posibles ===== ")
                print(" ========================")
                print("1- Nueva Mano")
                print(" ========================")