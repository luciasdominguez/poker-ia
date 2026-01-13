import sys
import os

# Añadir el directorio actual al path para que Python encuentre 'poker_engine'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ejecutar el juego
import poker_engine.Game
