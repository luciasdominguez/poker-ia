import poker_engine.data_models as dm
from poker_engine.GameMaster import Crupier
from poker_engine.console_interface import Table

player1 = dm.HumanPlayer("1", 1000)
player2 = dm.HumanPlayer("2", 1000)
player3 = dm.HumanPlayer("3", 1000)

game = dm.GameState([player1, player2, player3],50)

logic = Crupier(game)
interface = Table(game)

while True:
    interface.interfaz_basica()
    logic.ciclo_juego()