from dataclasses import dataclass, field
from Game.constants import YARD, PIECES_PER_PLAYER
from enum import IntEnum

@dataclass
class Piece:
    player_id: int
    piece_id: int
    position: int = YARD

    def __str__(self) -> str:
        return (
            f"Player {self.player_id}, "
            f"Piece {self.piece_id}, "
            f"Position {self.position}"
        )

class Color(IntEnum):
    RED = 0
    GREEN = 1
    YELLOW = 2
    BLUE = 3

@dataclass
class Player:
    player_id: int
    pieces: list[Piece] = field(init=False)
    color: Color = field(init=False)

    def __post_init__(self):
        if type(self.player_id) is not int:
            raise TypeError("Player ID must be an integer")

        self.color = Color(self.player_id)
        self.pieces = [
            Piece(self.player_id, piece_id) for piece_id in range(PIECES_PER_PLAYER)
        ]
    
    def __str__(self) -> str:
        pieces_text = "\n".join(str(piece) for piece in self.pieces)
        return f"Player {self.player_id} with Color: {self.color.name}:\n{pieces_text}"

@dataclass
class GameState:
    players: list[Player]
    current_player_index: int = 0
    dice_roll: int | None = None

    def current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    def __str__(self) -> str:
        players_text = "\n".join(str(player) for player in self.players)
        return (
            f"GameState:\n"
            f"Players:\n{players_text}\n"
            f"Current Player: {self.current_player().player_id}\n"
            f"Dice Roll: {self.dice_roll}\n"
        )
    
def initial_state(num_players: int) -> 'GameState':
    if type(num_players) != int:
        raise TypeError("Number of players must be an integer")

    if num_players not in (2, 4):
        raise ValueError("Number of players must be either 2 or 4")
    
    players = [Player(player_id) for player_id in range(num_players)]
    return GameState(players=players)
