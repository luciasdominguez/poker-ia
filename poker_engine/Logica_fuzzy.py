import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def get_fuzzy_decision(win_prob, pot_odds, rel_stack, difficulty='hard'):
    # 1. Variables de entrada
    prob = ctrl.Antecedent(np.arange(0, 1.01, 0.05), 'probability')
    odds = ctrl.Antecedent(np.arange(0, 1.01, 0.05), 'odds')
    stack = ctrl.Antecedent(np.arange(0, 1.01, 0.05), 'stack')

    # Variables de salida
    decision = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'decision')
    aggressiveness = ctrl.Consequent(np.arange(0, 1.01, 0.05), 'aggressiveness')

    # 2. Funciones de pertenencia (General)
    
    # Probability
    prob['low'] = fuzz.trapmf(prob.universe, [0, 0, 0.3, 0.45])
    prob['medium'] = fuzz.trimf(prob.universe, [0.4, 0.55, 0.7])
    prob['high'] = fuzz.trapmf(prob.universe, [0.65, 0.8, 1, 1])
    
    # Odds
    odds['good'] = fuzz.trapmf(odds.universe, [0, 0, 0.25, 0.35])
    odds['bad'] = fuzz.trapmf(odds.universe, [0.3, 0.5, 1, 1])
    
    # Stack
    stack['short'] = fuzz.trapmf(stack.universe, [0, 0, 0.2, 0.4])
    stack['deep'] = fuzz.trapmf(stack.universe, [0.3, 0.6, 1, 1])

    # Actions
    decision['fold'] = fuzz.trimf(decision.universe, [0, 1, 3])
    decision['call'] = fuzz.trimf(decision.universe, [2.5, 4, 5.5])
    decision['raise'] = fuzz.trimf(decision.universe, [5, 6.5, 8])
    decision['all_in'] = fuzz.trimf(decision.universe, [7.5, 10, 10])

    aggressiveness['low'] = fuzz.trimf(aggressiveness.universe, [0, 0.2, 0.4])
    aggressiveness['high'] = fuzz.trimf(aggressiveness.universe, [0.5, 1, 1])

    # 3. REGLAS SEGUN DIFICULTAD
    rules = []
    
    if difficulty == 'easy':
        # --- EASY MODE (FISH) ---
        # Passive, Loose. Ignores odds mostly.
        
        # 1. Call nearly everything unless trash
        rules.append(ctrl.Rule(prob['medium'], (decision['call'], aggressiveness['low'])))
        # 2. Even low prob, if cheap, call
        rules.append(ctrl.Rule(prob['low'] & odds['good'], (decision['call'], aggressiveness['low'])))
        # 3. Only fold absolute trash if expensive
        rules.append(ctrl.Rule(prob['low'] & odds['bad'], (decision['fold'], aggressiveness['low'])))
        # 4. Only Raise with monsters (predictable)
        rules.append(ctrl.Rule(prob['high'], (decision['raise'], aggressiveness['low'])))
        # 5. Rarely All-in, maybe only if short and high
        rules.append(ctrl.Rule(stack['short'] & prob['high'], (decision['all_in'], aggressiveness['high'])))
        
    else: # 'hard' (Default Shark)
        # --- HARD MODE (SHARK) ---
        # The advanced, stack-aware logic
        
        # Survival
        rules.append(ctrl.Rule(stack['short'] & (prob['medium'] | prob['high']), (decision['all_in'], aggressiveness['high'])))
        rules.append(ctrl.Rule(stack['short'] & prob['low'], (decision['fold'], aggressiveness['low'])))
        # Deep Stack
        rules.append(ctrl.Rule(prob['high'] & stack['deep'], (decision['raise'], aggressiveness['high'])))
        rules.append(ctrl.Rule(prob['medium'] & odds['good'], (decision['call'], aggressiveness['low'])))
        rules.append(ctrl.Rule(prob['medium'] & odds['bad'], (decision['fold'], aggressiveness['low'])))
        rules.append(ctrl.Rule(prob['low'], (decision['fold'], aggressiveness['low'])))
        rules.append(ctrl.Rule(prob['low'] & odds['good'], (decision['call'], aggressiveness['low'])))

    # 4. Simulación
    poker_ctrl = ctrl.ControlSystem(rules)
    simulation = ctrl.ControlSystemSimulation(poker_ctrl)

    simulation.input['probability'] = win_prob
    simulation.input['odds'] = pot_odds
    simulation.input['stack'] = rel_stack

    try:
        simulation.compute()
        score = simulation.output['decision']
        res_bet = float(simulation.output['aggressiveness'])
        
        if score < 3.0: res_action = 3 # Fold
        elif score < 5.5: res_action = 1 # Call
        elif score < 8.0: res_action = 2 # Raise
        else:
            res_action = 2
            if score >= 8.0: res_bet = 1.0 # Force max bet -> All-in effect
        
        return res_action, res_bet
        
    except Exception:
        return 3, 0.0
