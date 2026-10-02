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
 
def shared_path(color: Color, position: int, destination: int) -> list[int]:
    if not isinstance(color, Color) or type(position) is not int or type(destination) is not int:
        raise TypeError("The type of color must be Color, position and destination must be int.")
    
    if position < YARD or position > FINISHED:
        raise ValueError(f"The position has to be between {YARD} and {FINISHED}.")
    if destination < YARD or destination > FINISHED:
        raise ValueError(f"The destination has to be between {YARD} and {FINISHED}.")
    if position >= destination:
        raise ValueError("The position has to be less than the destination.")

    squares = []

    for rel_pos in range(position + 1, destination + 1):
        abs_pos = to_absolute(color, rel_pos)

        if abs_pos is not None:
            squares.append(abs_pos)
    
    return squares

def has_blockade(state: GameState, square: int, player_id: int) -> bool:
    count = count_pieces_at(state, square, player_id)

    if count > 2:
        raise ValueError("Stacks larger than two are not supported yet")

    return count == 2

def opponent_blockade_at(state: GameState, square: int, player_id: int) -> bool:
    # For validation purposes.
    count_pieces_at(state, square, player_id)

    exist = False
    for player in state.players:
        if player.player_id == player_id:
            continue
        
        if has_blockade(state, square, player.player_id):
            exist = True
            break
    
    return exist

def single_path_blocked(state: GameState, player_id: int, position: int, destination: int) -> bool:
    if type(player_id) is not int or type(position) is not int or type(destination) is not int:
        raise TypeError("The type of player_id, position and destination must be int.")
    
    player_ids = [player.player_id for player in state.players]
    if player_id not in player_ids:
        raise ValueError("Player is not in this game")
    
    for player in state.players:
        if player.player_id == player_id:
            moving_player = player
            break
    
    squares = shared_path(moving_player.color, position, destination)
    for square in squares:
        if is_safe_square(square):
            continue
        if opponent_blockade_at(state, square, player_id):
            return True
    
    return False
