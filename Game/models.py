from dataclasses import dataclass, field
from Game.constants import YARD, PIECES_PER_PLAYER
from enum import IntEnum

@dataclass
class Piece:
    player_id: int # Identifies the player who owns this piece.
    piece_id: int # Piece ID within that player: 0–3.
    position: int = YARD # Current relative progress; starts in the yard.

    # Return a description for str(piece) or print(piece); do not change state.
    def __str__(self) -> str:
        return (
            f"Player {self.player_id}, "
            f"Piece {self.piece_id}, "
            f"Position {self.position}"
        )

class Color(IntEnum):
    # Values match our current player IDs and index color-specific board constants.
    RED = 0
    GREEN = 1
    YELLOW = 2
    BLUE = 3

@dataclass
class Player:
    player_id: int
    # Derived fields are excluded from the generated constructor's arguments.
    pieces: list[Piece] = field(init=False)
    color: Color = field(init=False)

    # Called automatically after player_id is assigned; creates fresh pieces per player.
    def __post_init__(self):
        if type(self.player_id) is not int:
            raise TypeError("Player ID must be an integer")

        self.color = Color(self.player_id)
        self.pieces = [
            Piece(self.player_id, piece_id) for piece_id in range(PIECES_PER_PLAYER)
        ]
    
    # Return the player's ID, color, and piece descriptions without changing state.
    def __str__(self) -> str:
        # Call each piece's __str__ and join its description with newlines.
        pieces_text = "\n".join(str(piece) for piece in self.pieces)
        return f"Player {self.player_id} with Color: {self.color.name}:\n{pieces_text}"

@dataclass
class GameState:
    players: list[Player] # Participating players in turn order.
    current_player_index: int = 0 # Index into players, not a player ID.
    # Current roll to resolve; None means no roll is pending.
    dice_roll: int | None = None
    # Later rolls already collected for this turn; a fresh list for each state.
    remaining_rolls: list[int] = field(default_factory=list)

    def current_player(self) -> Player:
        # Return the player at the current index without advancing the turn.
        return self.players[self.current_player_index]
    
    def __str__(self) -> str:
        # Return player descriptions, current player ID, and current roll as text.

        players_text = "\n".join(str(player) for player in self.players)
        return (
            f"GameState:\n"
            f"Players:\n{players_text}\n"
            f"Current Player: {self.current_player().player_id}\n"
            f"Dice Roll: {self.dice_roll}\n"
        )

@dataclass
class Move:
    # Record a single/pair choice; creating it neither moves 
    # pieces nor checks board legality.
    player_id: int
    piece_ids: tuple[int, ...]

    def __post_init__(self):
        # Validate ID types/ranges and selection size; 
        # game rules check state and roll later.

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

        # A pair must select two different pieces, never the same piece twice.
        if len(set(self.piece_ids)) != len(self.piece_ids):
            raise ValueError("A move cannot select the same piece twice")
        
        
    def __str__(self) -> str:
        return (
            f"Move:\n"
            f"Player ID: {self.player_id}\n"
            f"Piece IDs: {self.piece_ids}\n"
        )

@dataclass
class GameResult:
    # Store one game's summary in memory; file saving is handled separately.

    winner_id: int | None # Records the ID of the winner of the game, if there was one. 
    seed: int # Reproduce a game with the same code and settings.
    num_players: int # How many players played in the game, 2 or 4?
    starting_player_index: int # Starting seat's index in the players list, not a player ID.
    max_turns: int # Maximum turns we allowed in the game.
    turns_played: int # Full turn sequences started, including cancelled and winning turns.
    moves_played: int # Applied single/pair actions; excludes passes and cancelled rolls.
    truncated: bool # Stopped at the turn limit without a winner; not a declared draw.
    invalid_choices: int # How many choiced were rejected?
    forfeited_turns: int # How many turns were cut short after three rejected choices?


def initial_state(num_players: int) -> 'GameState':
    # Validate the player count, then create a state with fresh players and pieces.
    # Pieces start in the yard; the first player is current and no rolls are pending.
    
    if type(num_players) != int:
        raise TypeError("Number of players must be an integer")

    if num_players not in (2, 4):
        raise ValueError("Number of players must be either 2 or 4")
    
    players = [Player(player_id) for player_id in range(num_players)]
    return GameState(players=players)
