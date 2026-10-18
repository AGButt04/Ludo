import random

class Dice:

    def __init__(self, seed: int | None = None):
        # Create a private generator; an explicit seed makes its sequence repeatable.
        self.rng = random.Random(seed)
    
    def roll(self) -> int:
        # Generate the next integer from 1 to 6 inclusive; do not change GameState.
        return self.rng.randint(1, 6)
