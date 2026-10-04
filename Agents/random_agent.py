import random
from Game.models import GameState, Move

class RandomAgent:
    
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
    
    def choose_move(self, state: GameState, moves: list[Move]) -> Move | None:
        if moves:
            return self.rng.choice(moves)
        else:
            return None
