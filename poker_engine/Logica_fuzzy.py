import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def get_fuzzy_decision(win_prob, pot_odds, rel_stack):
    # 1. Variables de entrada y salida
    prob = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'probability')
    odds = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'odds')

    decision = ctrl.Consequent(np.arange(1, 5, 1), 'decision')
    aggressiveness = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'aggressiveness')

    # 2. Funciones de pertenencia
    prob['baja'] = fuzz.trimf(prob.universe, [0, 0, 0.5])
    prob['media'] = fuzz.trimf(prob.universe, [0.3, 0.5, 0.7])
    prob['alta'] = fuzz.trimf(prob.universe, [0.5, 1, 1])

    odds['bajo'] = fuzz.trimf(odds.universe, [0, 0, 0.4])
    odds['alto'] = fuzz.trimf(odds.universe, [0.3, 1, 1])

    decision['call'] = fuzz.trimf(decision.universe, [1, 1, 1.5])
    decision['raise'] = fuzz.trimf(decision.universe, [1.5, 2, 2.5])
    decision['fold'] = fuzz.trimf(decision.universe, [2.5, 3, 3.5])
    decision['allin'] = fuzz.trimf(decision.universe, [3.5, 4, 4])

    aggressiveness['baja'] = fuzz.trimf(aggressiveness.universe, [0, 0.2, 0.4])
    aggressiveness['media'] = fuzz.trimf(aggressiveness.universe, [0.3, 0.5, 0.7])
    aggressiveness['alta'] = fuzz.trimf(aggressiveness.universe, [0.6, 0.8, 1])

    # 3. REGLAS CORREGIDAS
    # Las consecuencias deben ser asignaciones directas a las variables de salida
    rule1 = ctrl.Rule(prob['alta'] & odds['bajo'], (decision['raise'], aggressiveness['media']))
    rule2 = ctrl.Rule(prob['baja'] & odds['alto'], (decision['fold'], aggressiveness['baja']))
    rule3 = ctrl.Rule(prob['media'], (decision['call'], aggressiveness['baja']))
    rule4 = ctrl.Rule(prob['alta'] & prob['media'], (decision['allin'], aggressiveness['alta']))

    # 4. Simulación
    poker_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
    simulation = ctrl.ControlSystemSimulation(poker_ctrl)

    simulation.input['probability'] = win_prob
    simulation.input['odds'] = pot_odds

    try:
        simulation.compute()
        # Defuzzificación
        res_action = int(round(simulation.output['decision']))
        res_bet = float(simulation.output['aggressiveness'])
        return res_action, res_bet
    except Exception:
        # Si falla por reglas no cubiertas, acción por defecto: Call
        return 1, 0.0