import poker_engine.data_models as dm
from poker_engine.GameMaster import Crupier
from poker_engine.console_interface import Table
import time

game = dm.GameState([], 50)

# Configurar Dificultad
print("=== POKER IA ===")
print("Selecciona Dificultad de la IA:")
print("1. Fácil (Modo Fish) - Pasivo y Relajado")
print("2. Difícil (Modo Shark) - Agresivo y Calculador")
choice = input("Elige (1/2): ")
difficulty = 'easy' if choice == '1' else 'hard'

# Crear Jugadores
# Un humano y dos bots
player1 = dm.HumanPlayer("Hero", 1000)
player2 = dm.AIPlayer("Bot_1", 1000, game, difficulty)
player3 = dm.AIPlayer("Bot_2", 1000, game, difficulty)

game = dm.GameState([player1, player2, player3], 50)

logic = Crupier(game)
interface = Table(game)


while True:
    interface.interfaz_basica()
    logic.ciclo_juego()

    # Si el turno es de una IA, esperamos un segundo para leer qué pasó
    if not isinstance(game.players[game.turn_to_act_index], dm.HumanPlayer):
        time.sleep(1)
