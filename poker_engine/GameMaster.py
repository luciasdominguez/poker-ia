import poker_engine.data_models as dm
import poker_engine.poker_rules as pk
from enum import Enum


# Contiene el ciclo principal de juego y algunas funciones para hacerlo funcionar
class Crupier:
    def __init__(self, game: dm.GameState):
        self.game = game
        self.dealed = False
        self.evaluator = pk.HandEvaluator()

    def deal_players(self):
        for i in range(2):
            for player in self.game.players:
                if  player.is_active:
                    player.hand.append(self.game.deck.deal())

    def deal_community(self):
        self.game.community_cards.append(self.game.deck.deal())

    def burn_card(self):
        self.game.burned_cards.append(self.game.deck.deal())

    def blinds(self):
        #Hacer la apuesta
        self.game.players[self.game.turn_to_act_index].current_bet = self.game.smallBlind
        self.game.players[((self.game.turn_to_act_index + 1) % len(self.game.players))].current_bet = self.game.bigBlind
        #Retirar el dinero de los jugadores
        self.game.players[self.game.turn_to_act_index].stack -= self.game.smallBlind
        self.game.players[((self.game.turn_to_act_index+1) % len(self.game.players))].stack -= self.game.bigBlind
        #Incluir la apuesta en el bote
        self.game.current_raise_to_match = self.game.bigBlind
        
        self.game.pot = self.game.smallBlind + self.game.bigBlind
        #Darle el turno al primer jugador (despues de las ciegas)
        self.game.last_raiser = ((self.game.turn_to_act_index+1) % len(self.game.players))
        self.game.turn_to_act_index = (self.game.turn_to_act_index + 2) % len(self.game.players)

    def all_has_called(self): #Revisar si todos los jugadores han realizado al menos una acción
        for player in self.game.players:
            if player.is_active == True:
                if player.has_called == False:
                    return False
        return True

    def ciclo_juego(self):
        match self.game.round:
            case dm.Round.PreFlop:
                if self.dealed == False:
                    self.deal_players()

                    self.blinds()

                    self.dealed = True
                    return
                
                #Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(self.game.current_raise_to_match)
                self.game.pot += amount_raised
                if new_high_raise != self.game.current_raise_to_match and not self.game.players[self.game.turn_to_act_index].is_all_in:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index

                
                #Cambiar de ronda si corresponde, en caso contrario, cambiar jugador
                if self.all_has_called() and  (self.game.turn_to_act_index == self.game.last_raiser):
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.Flop
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players) #Cambiar de jugador
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.Flop:
                if self.dealed == False:
                    self.burn_card()
                    for i in range(3):
                        self.deal_community()
                    self.dealed = True
                    return

                #Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(self.game.current_raise_to_match)
                self.game.pot += amount_raised
                if new_high_raise != self.game.current_raise_to_match and not self.game.players[self.game.turn_to_act_index].is_all_in:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index

                #Cambiar de ronda si corresponde, en caso contrario, cambiar jugador
                if self.all_has_called() and  (self.game.turn_to_act_index == self.game.last_raiser):
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.Turn
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players) #Cambiar de jugador
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.Turn:
                if self.dealed == False:
                    self.burn_card()
                    self.deal_community()
                    self.dealed = True
                    return
                    
                #Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(self.game.current_raise_to_match)
                self.game.pot += amount_raised
                if new_high_raise != self.game.current_raise_to_match and not self.game.players[self.game.turn_to_act_index].is_all_in:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index

                #Cambiar de ronda si corresponde, en caso contrario, cambiar jugador
                if self.all_has_called() and  (self.game.turn_to_act_index == self.game.last_raiser):
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.River
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players) #Cambiar de jugador
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.River:
                if self.dealed == False:
                    self.burn_card()
                    self.deal_community()
                    self.dealed = True
                    return
                
                #Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(self.game.current_raise_to_match)
                self.game.pot += amount_raised
                if new_high_raise != self.game.current_raise_to_match and not self.game.players[self.game.turn_to_act_index].is_all_in:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index

                #Cambiar de ronda si corresponde, en caso contrario, cambiar jugador
                if self.all_has_called() and  (self.game.turn_to_act_index == self.game.last_raiser):
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.ShowHand
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players) #Cambiar de jugador
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.ShowHand:
                #Evaluar manos (Se sigue usando dealed como flag para valorar si es el primer ciclo en esta ronda)
                if self.dealed == False:
                    for player in self.game.players:
                        if player.is_active == True:
                            player.evaluation = self.evaluator.evaluate_hand(player_hand = player.hand, community_cards = self.game.community_cards)

                    #Recompensar al ganador o ganadores si hay side pots (Condicionar a reinicio)
                    while self.game.yet_to_evaluate() and self.game.pot > 0:
                        #Comparar cartas
                        best_index = None
                        for index, player in enumerate(self.game.players):
                            if player.is_active:
                                best_index = index #Tomar el primer judador activo
                                break

                        for i in range(best_index, len(self.game.players)):
                            if self.game.players[i].is_active == True and i != best_index:
                                if self.game.players[i].evaluation > self.game.players[best_index].evaluation:
                                    best_index = i
                        #Identificar si hay algun side_pot y su tamaño
                        minimum_bet_player_index, minimum_bet = self.game.minimum_bet_player()
                        side_pot = minimum_bet * self.game.number_of_active()
                        #Añadir el dinero del sidepot al mejor jugador y eliminarlo del principal
                        self.game.players[best_index].stack += side_pot
                        self.game.pot -= side_pot
                        #Guardar el jugador y cuanto ha ganado para su visualizacion
                        self.game.winner_players.append(self.game.players[best_index].name)
                        self.game.amount_won.append(side_pot)
                        #Desactivar al jugador que lo creo
                        self.game.players[minimum_bet_player_index].is_evaluated = True

                    self.dealed = True
                
                else:
                    opcion = input("Please, choose an option from the provided list, using its assigned number. Choose Action: ")
                    opcion = int(opcion)
                    while opcion != 1:
                        opcion = input("Please, choose an option from the provided list, using its assigned number. Choose Action: ")
                    opcion = int(opcion)

                    self.dealed = False
                    self.game.reset_for_new_hand()
                    self.game.round = dm.Round.PreFlop

