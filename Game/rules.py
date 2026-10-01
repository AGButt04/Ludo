from Game.constants import YARD, TRACK_START, FINISHED, TRACK_END, TRACK_LENGTH, START_SQUARES, SAFE_SQUARES
from Game.models import Color, GameState, Piece, Player

def destination_for_roll(position: int, dice_roll: int):
    if type(position) is not int or type(dice_roll) is not int:
        raise TypeError("The type of the dice_roll and position has to be an integer.")
    
    if not YARD <= position <= FINISHED:
        raise ValueError("The position has to be between 0 and 57.")
    if not 1 <= dice_roll <= 6:
        raise ValueError("The dice roll has to be between 1 and 6.")
    
    if position == 0 and dice_roll == 6:
        return TRACK_START
    elif position == 0:
        return None
    elif position == FINISHED:
        return None
    else:
        new_pos = position + dice_roll
        return new_pos if (new_pos <= FINISHED) else None


def to_absolute(color: Color, position: int) -> int | None:
    if not isinstance(color, Color) or type(position) is not int:
        raise TypeError("The type of color should be Color and position be int.")
    
    if position < YARD or position > FINISHED:
        raise ValueError(f"The Value must be in between {YARD} and {FINISHED}.")

    if position < TRACK_START or position > TRACK_END:
        return None
    
    start = START_SQUARES[color]
    return ((start - 1 + position - 1) % TRACK_LENGTH) + 1

def pieces_at(state: GameState, square: int) -> list[Piece]:
    if type(square) is not int:
        raise TypeError("The square position must be an integer.")
    if not 1 <= square <= TRACK_LENGTH:
        raise ValueError(f"Square must be between 1 and {TRACK_LENGTH}")
    
    pieces = []
    players = state.players

    for player in players:
        for piece in player.pieces:
            pos = to_absolute(player.color, piece.position)

            if pos == square:
                pieces.append(piece)
    
    return pieces

def is_safe_square(square: int) -> bool:
    if type(square) is not int:
        raise TypeError("The square position must be an integer.")
    if not 1 <= square <= TRACK_LENGTH:
        raise ValueError(f"Square must be between 1 and {TRACK_LENGTH}")
    
    return square in SAFE_SQUARES

def count_pieces_at(state: GameState, square: int, player_id: int) -> int:
    if type(player_id) is not int:
        raise TypeError("Player ID must be an integer")

    player_ids = [player.player_id for player in state.players]
    if player_id not in player_ids:
        raise ValueError("Player is not in this game")

    pieces = pieces_at(state, square)
    count = 0
    for piece in pieces:
        if piece.player_id == player_id:
            count += 1
    
    return count