def get_fuzzy_decision(win_prob, pot_odds, relative_stack):
    """
    Este método lo programa la otra persona.
    Entradas: valores de 0.0 a 1.0
    Salidas: (Accion, Cantidad)
    """
    # Aquí la otra persona usará una librería como 'scikit-fuzzy' o
    # reglas IF-THEN manuales.

    action = 1  # 1: Call/Pass, 2: Raise, 3: Fold
    bet_multiplier = 0  # Cuánto más subir si la acción es Raise

    # Ejemplo de regla interna:
    if win_prob > 0.8 and pot_odds < 0.3:
        action = 2
        bet_multiplier = 0.5  # Subir un 50% del stack

    return action, bet_multiplier