import poker_engine.data_models as dm
import poker_engine.poker_rules as pk
from enum import Enum


# Contiene el ciclo principal de juego y algunas funciones para hacerlo funcionar
class Crupier:
    def __init__(self, game: dm.GameState):
        self.game = game
        self.dealed = False
        self.evaluator = pk.HandEvaluator()

    def check_early_win(self):
        # Si solo queda un jugador activo, gana todo el bote inmediatamente
        if self.game.number_of_active() == 1:
            # Encontrar al ganador
            winner = None
            for p in self.game.players:
                if p.is_active:
                    winner = p
                    break
            
            if winner:
                # Todo el bote para el (incluyendo side pots si hubiera, pero si todos foldean, side pots se pueden simplificar)
                # Ojo: resolve_side_pots podria haber separado dinero.
                # Si es Win By Fold, el ganador se lleva TODO el dinero "vivo" de la mesa.
                # El dinero de los side pots son de gente que ya esta All-in?
                # Si estan All-in, NO han hecho fold. Active includes All-in players?
                # number_of_active normalmente incluye all-in si is_active=True.
                # Si alguien hizo Fold, is_active=False.
                # Si quedan players All-in (is_active=True), entonces NO es early win, hay showdown.
                
                # number_of_active logic in data_models:
                # if player.is_active == True: count += 1.
                # Folded players set is_active=False.
                # So if count=1, only 1 person has cards. Others folded.
                # Winner takes game.pot + sums of side_pots?
                
                # Por simplicidad, consolidar todo en game.pot antes de darlo, o iterar.
                total_pot = self.game.pot
                for sp in self.game.side_pots: # Si hubiera
                     total_pot += sp.amount
                
                winner.stack += total_pot
                self.game.winner_players.append(winner.name)
                self.game.amount_won.append(total_pot)
                
                self.game.pot = 0
                self.game.side_pots = []
                self.game.round = dm.Round.EndGame # End Hand
                return True
        return False

    def deal_players(self):
        for i in range(2):
            for player in self.game.players:
                if player.is_active:
                    player.hand.append(self.game.deck.deal())

    def deal_community(self):
        self.game.community_cards.append(self.game.deck.deal())

    def burn_card(self):
        self.game.burned_cards.append(self.game.deck.deal())

    def blinds(self):
        # Hacer la apuesta
        sb_player = self.game.players[self.game.turn_to_act_index]
        bb_player = self.game.players[((self.game.turn_to_act_index + 1) % len(self.game.players))]
        
        sb_player.current_bet = self.game.smallBlind
        sb_player.total_bet_in_hand += self.game.smallBlind # Track total
        
        bb_player.current_bet = self.game.bigBlind
        bb_player.total_bet_in_hand += self.game.bigBlind # Track total
        
        # Retirar el dinero de los jugadores
        sb_player.stack -= self.game.smallBlind
        bb_player.stack -= self.game.bigBlind
        
        # Incluir la apuesta en el bote
        self.game.current_raise_to_match = self.game.bigBlind
        
        self.game.pot = self.game.smallBlind + self.game.bigBlind
        # Darle el turno al primer jugador (despues de las ciegas)
        self.game.last_raiser = ((self.game.turn_to_act_index + 1) % len(self.game.players))
        self.game.turn_to_act_index = (self.game.turn_to_act_index + 2) % len(self.game.players)

    def all_has_called(self):  # Revisar si todos los jugadores han realizado al menos una acción
        for player in self.game.players:
            if player.is_active == True:
                if player.has_called == False:
                    return False
        return True

    def resolve_side_pots(self):
        # 1. Recolectar todas las apuestas totales de los jugadores activos o all-in
        
        active_bets = []
        for p in self.game.players:
            if p.total_bet_in_hand > 0:
                 active_bets.append(p.total_bet_in_hand)
        
        unique_bets = sorted(list(set(active_bets)))
        
        # Resetear side_pots actuales
        self.game.side_pots = []
        
        current_level_bet = 0
        
        for bet_level in unique_bets:
            pot_amount = 0
            eligible_players = []
            
            # Cuanto se contribuye a este nivel (diferencia con el anterior)
            contribution = bet_level - current_level_bet
            if contribution <= 0: continue
            
            contributing_players_count = 0

            for p in self.game.players:
                # Si el jugador aposto al menos hasta este nivel, contribuye
                if p.total_bet_in_hand >= bet_level:
                    pot_amount += contribution
                    contributing_players_count +=1
                    if p.is_active and not p.hand == []: # Solo si sigue jugando (no fold)
                         eligible_players.append(p.name)
                elif p.total_bet_in_hand > current_level_bet:
                    # El jugador aposto algo intermedio pero menos que este nivel
                    partial = p.total_bet_in_hand - current_level_bet
                    pot_amount += partial
                    if p.is_active and not p.hand == []: # Raro caso si no hizo fold
                        # Si no llego al nivel, tecnicamente no puede optar a este bote completo
                        # PERO en poker side pots se definen por niveles de all-in.
                        # Si alguien esta all-in por debajo de bet_level, NO entra en `eligible_players` de ESTE nivel superior.
                        pass

            # Regla de devolucion: Si solo 1 jugador contribuyo a este nivel (y nadie mas lo igualo ni parcialmente),
            # se le devuelve ese dinero.
            if contributing_players_count == 1 and eligible_players:
                 # Encontrar al jugador y devolverle la pasta
                 solo_player_name = eligible_players[0]
                 for p in self.game.players:
                     if p.name == solo_player_name:
                         p.stack += pot_amount
                 pass
            elif pot_amount > 0:
                # Si no hay jugadores elegibles (todos los contribuidores foldearon),
                # el dinero es "Dead Money" y debe bajar al bote anterior (Main Pot) donde haya gente.
                if not eligible_players:
                    if self.game.side_pots:
                        # Añadir al ultimo bote valido (el mas alto hasta ahora, o el main)
                        # Nota: side_pots se llenan de menor apuesta a mayor. [-1] es el mas alto anterior.
                        # Pero conceptualmente si todos foldearon lo alto, el dinero va al "Active Pot" mas alto.
                        self.game.side_pots[-1].amount += pot_amount
                    else:
                        # Si es el primer nivel y nadie es elegible... (Raro, significaria 0 active players)
                        # Crear side pot igual, distribute_pot fallara pero no hay a quien darselo.
                        # O darselo al ultimo que foldeo? No, check_early_win deberia haber saltado.
                        # Asumimos que hay un side_pot previo si hay jugadores All-in activos.
                        self.game.side_pots.append(dm.SidePot(pot_amount, eligible_players))
                else:
                    # Si es el primer nivel y nadie de los que puso dinero esta activo (todos foldearon)
                    # El dinero se lo llevan los supervivientes (los que sigan activos aunque hayan puesto menos o nada - blinds/allin 0)
                    survivors = [p.name for p in self.game.players if p.is_active]
                    self.game.side_pots.append(dm.SidePot(pot_amount, survivors))
            
            current_level_bet = bet_level

    def distribute_pot(self):
         self.resolve_side_pots()
         
         # Evaluar manos de todos los jugadores activos
         for player in self.game.players:
            if player.is_active:
                player.evaluation = self.evaluator.evaluate_hand(player.hand, self.game.community_cards)

         # Iterar sobre cada side pot y buscar ganador
         for side_pot in self.game.side_pots:
             if not side_pot.eligible_players:
                 continue 
             
             candidates = [p for p in self.game.players if p.name in side_pot.eligible_players]
             
             if not candidates: continue

             # Encontrar la mejor mano
             best_eval = candidates[0].evaluation
             winners = [candidates[0]]
             
             for p in candidates[1:]:
                 # Asumiendo que evaluation implementa comparacion correcta. 
                 # Si p > best: nuevo ganador unico.
                 # Si p == best: split pot.
                 # Necesitamos que HandEvaluator soporte igualdad correctamente.
                 # Modificar poker_rules si es necesario o usar comparacion manual.
                 if p.evaluation > best_eval:
                     best_eval = p.evaluation
                     winners = [p]
                 elif not (best_eval > p.evaluation): # Si best no es mayor que p, y p no mayor que best -> EMPATE
                      winners.append(p)
             
             share = side_pot.amount // len(winners)
             remaining = side_pot.amount % len(winners)

             for w in winners:
                 w.stack += share
                 self.game.winner_players.append(w.name)
                 self.game.amount_won.append(share)
             
             # Dar remanente al primero (por posicion, inutisto pero estandar simple)
             if remaining > 0:
                 winners[0].stack += remaining
                 
         self.game.pot = 0

    def ciclo_juego(self):
        match self.game.round:
            case dm.Round.PreFlop:
                if self.dealed == False:
                    self.deal_players()

                    self.blinds()

                    self.dealed = True
                    return

                # Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(
                    self.game.current_raise_to_match)
                self.game.pot += amount_raised
                self.game.players[self.game.turn_to_act_index].total_bet_in_hand += amount_raised # Track total
                
                if self.check_early_win(): return # Check if everyone else folded
                
                if new_high_raise != self.game.current_raise_to_match:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index
                    # Si hubo subida, invalidar has_called para el resto para obligarles a actuar
                    for p in self.game.players:
                        if p != self.game.players[self.game.turn_to_act_index]:
                            p.has_called = False

                # Cambiar de ronda si corresponde
                # PreFlop: Termina cuando el turno vuelve al last_raiser y este ya ha actuado (BB Option)
                # PostFlop: Termina cuando el next_turn es el last_raiser
                next_turn_index = (self.game.turn_to_act_index + 1) % len(self.game.players)
                round_complete = False
                
                if self.all_has_called():
                    if self.game.round == dm.Round.PreFlop and self.game.turn_to_act_index == self.game.last_raiser:
                        round_complete = True
                    elif next_turn_index == self.game.last_raiser:
                        round_complete = True

                if round_complete:
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.Flop
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = next_turn_index  # Cambiar de jugador
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.Flop:
                if self.dealed == False:
                    self.burn_card()
                    for i in range(3):
                        self.deal_community()
                    self.dealed = True
                    return

                # Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(
                    self.game.current_raise_to_match)
                self.game.pot += amount_raised
                self.game.players[self.game.turn_to_act_index].total_bet_in_hand += amount_raised # Track total
                
                if self.check_early_win(): return

                if new_high_raise != self.game.current_raise_to_match:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index
                    for p in self.game.players:
                        if p != self.game.players[self.game.turn_to_act_index]:
                            p.has_called = False

                next_turn_index = (self.game.turn_to_act_index + 1) % len(self.game.players)
                round_complete = False
                
                # Check PostFlop / PreFlop unified logic (Although this block is Flop, sticking to unified safe logic)
                if self.all_has_called():
                    if self.game.round == dm.Round.PreFlop and self.game.turn_to_act_index == self.game.last_raiser:
                        round_complete = True
                    elif next_turn_index == self.game.last_raiser:
                        round_complete = True

                if round_complete:
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.Turn
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = next_turn_index
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.Turn:
                if self.dealed == False:
                    self.burn_card()
                    self.deal_community()
                    self.dealed = True
                    return

                # Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(
                    self.game.current_raise_to_match)
                self.game.pot += amount_raised
                self.game.players[self.game.turn_to_act_index].total_bet_in_hand += amount_raised # Track total
                
                if self.check_early_win(): return

                if new_high_raise != self.game.current_raise_to_match:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index
                    for p in self.game.players:
                        if p != self.game.players[self.game.turn_to_act_index]:
                            p.has_called = False

                next_turn_index = (self.game.turn_to_act_index + 1) % len(self.game.players)
                round_complete = False
                
                if self.all_has_called():
                    if self.game.round == dm.Round.PreFlop and self.game.turn_to_act_index == self.game.last_raiser:
                        round_complete = True
                    elif next_turn_index == self.game.last_raiser:
                        round_complete = True

                if round_complete:
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.River
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = next_turn_index
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.River:
                if self.dealed == False:
                    self.burn_card()
                    self.deal_community()
                    self.dealed = True
                    return

                # Pedir accion a jugador e incrementar bote si es necesario
                new_high_raise, amount_raised = self.game.players[self.game.turn_to_act_index].action(
                    self.game.current_raise_to_match)
                self.game.pot += amount_raised
                self.game.players[self.game.turn_to_act_index].total_bet_in_hand += amount_raised # Track total
                
                if self.check_early_win(): return

                if new_high_raise != self.game.current_raise_to_match:
                    self.game.current_raise_to_match = new_high_raise
                    self.game.last_raiser = self.game.turn_to_act_index
                    for p in self.game.players:
                        if p != self.game.players[self.game.turn_to_act_index]:
                            p.has_called = False

                next_turn_index = (self.game.turn_to_act_index + 1) % len(self.game.players)
                round_complete = False
                
                if self.all_has_called():
                    if self.game.round == dm.Round.PreFlop and self.game.turn_to_act_index == self.game.last_raiser:
                        round_complete = True
                    elif next_turn_index == self.game.last_raiser:
                        round_complete = True

                if round_complete:
                    self.game.turn_to_act_index = self.game.small_blind_indx
                    self.game.last_raiser = self.game.small_blind_indx
                    self.dealed = False
                    self.game.round = dm.Round.ShowHand
                    self.dealed = False
                    for player in self.game.players:
                        player.change_round()
                else:
                    self.game.turn_to_act_index = next_turn_index
                    while not self.game.players[self.game.turn_to_act_index].is_active:
                        self.game.turn_to_act_index = (self.game.turn_to_act_index + 1) % len(self.game.players)

            case dm.Round.ShowHand:
                # Evaluar manos (Se sigue usando dealed como flag para valorar si es el primer ciclo en esta ronda)
                if self.dealed == False:
                    self.distribute_pot()
                    self.dealed = True

                else:
                    opcion = input(
                        "Please, choose an option from the provided list, using its assigned number. Choose Action: ")
                    opcion = int(opcion)
                    while opcion != 1:
                        opcion = input(
                            "Please, choose an option from the provided list, using its assigned number. Choose Action: ")
                    opcion = int(opcion)

                    self.dealed = False
                    self.game.reset_for_new_hand()
                    self.game.round = dm.Round.PreFlop