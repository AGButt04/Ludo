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

@dataclass
class Move:
    player_id: int
    piece_ids: tuple[int, ...]

    def __post_init__(self):
        if type(self.player_id) != int:
            raise TypeError("Player ID must be an integer")

        if type(self.piece_ids) != tuple:
            raise TypeError("Piece IDs must be a tuple")

        if not 0 <= self.player_id <= 3:
            raise ValueError("Player ID must be between 0 and 3")
        
        if len(self.piece_ids) not in (1, 2):
            raise ValueError("A move must select one or two pieces")

        if any(type(piece_id) is not int for piece_id in self.piece_ids):
            raise TypeError("Each piece ID must be an integer")

        if not all(0 <= piece_id < PIECES_PER_PLAYER for piece_id in self.piece_ids):
            raise ValueError("Piece IDs must be between 0 and 3")

        if len(set(self.piece_ids)) != len(self.piece_ids):
            raise ValueError("A move cannot select the same piece twice")
        
        
    def __str__(self) -> str:
        return (
            f"Move:\n"
            f"Player ID: {self.player_id}\n"
            f"Piece IDs: {self.piece_ids}\n"
        )
    
def initial_state(num_players: int) -> 'GameState':
    if type(num_players) != int:
        raise TypeError("Number of players must be an integer")

    if num_players not in (2, 4):
        raise ValueError("Number of players must be either 2 or 4")
    
    players = [Player(player_id) for player_id in range(num_players)]
    return GameState(players=players)
