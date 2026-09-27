import random

class Dice:

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
    
    def roll(self) -> int:
        return self.rng.randint(1, 6)