import os
import poker_engine.data_models as dm
from enum import Enum

#Contiene las funciones para pintar la mesa (interfaz por consola con el usuario)
class Table:
    def __init__(self, game: dm.GameState):
        self.game = game
    
    def limpiar_consola(self):
        print("\033c", end="")

    def interfaz_basica(self):
        match self.game.round:
            case dm.Round.PreFlop:
                self.limpiar_consola()
                #Caracteristicas globales de la partida:
                print(" ===== Table Estate ===== ")
                print(" Round: Pre-Flop ")
                print(f" Main Pot: {self.game.pot}")
                print(f" Community Cards: {self.game.community_cards}")
                print(" ========================") 

                #Características del propio jugador:
                print(f" ===== Player {self.game.turn_to_act_index+1} ===== ")
                print(" ========================") 
                print(f" Stack: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Bet: {self.game.players[self.game.turn_to_act_index].current_bet}")
                print(f" Cards: {self.game.players[self.game.turn_to_act_index].hand}")
                print(" ========================") 

                #Acciones a realizar
                print(f" ===== Possible Actions ===== ")
                print(" ========================") 
                print("1- Call/Pass")
                print("2 - Raise")
                print("3 - Fold")
                print("4 - All in")
                print(" ========================") 

            case dm.Round.Flop:
                self.limpiar_consola()
                #Caracteristicas globales de la partida:
                print(" ===== Table Estate ===== ")
                print(" Round: Flop ")
                print(f" Main Pot: {self.game.pot}")
                print(f" Community Cards: {self.game.community_cards}")
                print(" ========================") 

                #Características del propio jugador:
                print(f" ===== Player {self.game.turn_to_act_index+1} ===== ")
                print(" ========================") 
                print(f" Stack: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Bet: {self.game.players[self.game.turn_to_act_index].current_bet}")
                print(f" Cards: {self.game.players[self.game.turn_to_act_index].hand}")
                print(" ========================") 

                #Acciones a realizar
                print(f" ===== Possible Actions ===== ")
                print(" ========================") 
                print("1- Call/Pass")
                print("2 - Raise")
                print("3 - Fold")
                print("4 - All in")
                print(" ========================")

            case dm.Round.Turn:
                self.limpiar_consola()
                #Caracteristicas globales de la partida:
                print(" ===== Table Estate ===== ")
                print(" Round: Turn")
                print(f" Main Pot: {self.game.pot}")
                print(f" Community Cards: {self.game.community_cards}")
                print(" ========================") 

                #Características del propio jugador:
                print(f" ===== Player {self.game.turn_to_act_index+1} ===== ")
                print(" ========================") 
                print(f" Stack: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Bet: {self.game.players[self.game.turn_to_act_index].current_bet}")
                print(f" Cards: {self.game.players[self.game.turn_to_act_index].hand}")
                print(" ========================") 

                #Acciones a realizar
                print(f" ===== Possible Actions ===== ")
                print(" ========================") 
                print("1- Call/Pass")
                print("2 - Raise")
                print("3 - Fold")
                print("4 - All in")
                print(" ========================") 
            

            case dm.Round.River:
                self.limpiar_consola()
                #Caracteristicas globales de la partida:
                print(" ===== Table Estate ===== ")
                print(" Round: River")
                print(f" Main Pot: {self.game.pot}")
                print(f" Community Cards: {self.game.community_cards}")
                print(" ========================") 

                #Características del propio jugador:
                print(f" ===== Player {self.game.turn_to_act_index+1} ===== ")
                print(" ========================") 
                print(f" Stack: {self.game.players[self.game.turn_to_act_index].stack}")
                print(f" Bet: {self.game.players[self.game.turn_to_act_index].current_bet}")
                print(f" Cards: {self.game.players[self.game.turn_to_act_index].hand}")
                print(" ========================") 

                #Acciones a realizar
                print(f" ===== Possible Actions ===== ")
                print(" ========================") 
                print("1- Call/Pass")
                print("2 - Raise")
                print("3 - Fold")
                print("4 - All in")
                print(" ========================") 

            case dm.Round.ShowHand:
                self.limpiar_consola()
                #Caracteristicas globales de la partida:
                print(" ===== Table Estate ===== ")
                print(" Round: Showing Hands ")
                print(f" Main Pot: {self.game.pot}")
                print(f" Community Cards: {self.game.community_cards}")
                print(" ========================") 

                #Manos de cada jugador
                print(" ===== Player Cards ===== ")
                print(" ========================") 
                for player in self.game.players:
                    if player.is_active == True:
                        print(f"Player {player.name}: {player.hand}")

                #Mostrar ganadores y cantidad:
                print(" ===== Winners =====")
                print(" ========================") 
                print(f"Players: {self.game.winner_players}")
                print(f"Amount won: {self.game.amount_won}")
                print(" ========================") 

                #Acciones a realizar
                print(f" ===== Possible Actions ===== ")
                print(" ========================") 
                print("1- Restart")
                print(" ========================") 