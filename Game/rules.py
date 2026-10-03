from Game.constants import YARD, TRACK_START, FINISHED, TRACK_END, TRACK_LENGTH, START_SQUARES, SAFE_SQUARES, HOME_START, HOME_END
from Game.models import Color, GameState, Piece, Player, Move
from itertools import combinations

def validate_int_range(value: int, minimum: int, maximum: int, name: str) -> None:
    """Reject non-integers (including booleans) and out-of-range values."""
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")


def validate_roll(dice_roll: int) -> None:
    validate_int_range(dice_roll, 1, 6, "Dice roll")


def validate_position(position: int) -> None:
    """Relative progress includes yard, home path, and finish."""
    validate_int_range(position, YARD, FINISHED, "Position")


def validate_square(square: int) -> None:
    """Absolute squares belong only to the shared track."""
    validate_int_range(square, 1, TRACK_LENGTH, "Square")


def validate_color(color: Color) -> None:
    if not isinstance(color, Color):
        raise TypeError("Color must be a Color")


def get_player(state: GameState, player_id: int) -> Player:
    """Find a participant by ID, regardless of seating/list order."""
    validate_int_range(player_id, 0, 3, "Player ID")
    for player in state.players:
        if player.player_id == player_id:
            return player
    raise ValueError("Player is not in this game")


def get_move_pieces(state: GameState, move: Move) -> tuple[Player, list[Piece]]:
    """Resolve a Move to its player and selected pieces; do not change state."""
    if not isinstance(move, Move):
        raise TypeError("Move must be a Move")

    player = get_player(state, move.player_id)
    selected_pieces = []

    for piece in player.pieces:
        if piece.piece_id in move.piece_ids:
            selected_pieces.append(piece)

    if len(selected_pieces) != len(move.piece_ids):
        raise ValueError("Not all selected pieces were found")
    
    return player, selected_pieces

def destination_for_roll(position: int, dice_roll: int):
    validate_position(position)
    validate_roll(dice_roll)

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
    validate_color(color)
    validate_position(position)

    if position < TRACK_START or position > TRACK_END:
        return None
    
    start = START_SQUARES[color]
    return ((start - 1 + position - 1) % TRACK_LENGTH) + 1

def pieces_at(state: GameState, square: int) -> list[Piece]:
    validate_square(square)
    pieces = []
    players = state.players

    for player in players:
        for piece in player.pieces:
            pos = to_absolute(player.color, piece.position)

            if pos == square:
                pieces.append(piece)
    
    return pieces

def is_safe_square(square: int) -> bool:
    validate_square(square)
    return square in SAFE_SQUARES

def count_pieces_at(state: GameState, square: int, player_id: int) -> int:
    get_player(state, player_id)

    pieces = pieces_at(state, square)
    count = 0
    for piece in pieces:
        if piece.player_id == player_id:
            count += 1
    
    return count
 
def shared_path(color: Color, position: int, destination: int) -> list[int]:
    validate_color(color)
    validate_position(position)
    validate_position(destination)
    
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
    get_player(state, player_id)
    validate_square(square)

    exist = False
    for player in state.players:
        if player.player_id == player_id:
            continue
        
        if has_blockade(state, square, player.player_id):
            exist = True
            break
    
    return exist

def single_path_blocked(state: GameState, player_id: int, position: int, destination: int) -> bool:
    moving_player = get_player(state, player_id)

    squares = shared_path(moving_player.color, position, destination)
    for square in squares:
        if is_safe_square(square):
            continue
        if opponent_blockade_at(state, square, player_id):
            return True
    
    return False

def move_destination(state: GameState, move: Move, dice_roll: int) -> int | None:
    validate_roll(dice_roll)
    player, selected_pieces = get_move_pieces(state, move)

    if len(selected_pieces) == 1:
        return destination_for_roll(selected_pieces[0].position, dice_roll)
    else:
        first, second = selected_pieces

        if first.position != second.position:
            return None
        if first.position in (YARD, FINISHED):
            return None
        if dice_roll % 2 != 0:
            return None
        
        destination = first.position + dice_roll // 2
        return destination if destination <= FINISHED else None

def can_land(state: GameState, move: Move, destination: int) -> bool:
    player, selected_pieces = get_move_pieces(state, move)
    validate_int_range(destination, TRACK_START, FINISHED, "Destination")
    
    if destination == FINISHED:
        return True
    
    own_count = 0
    for piece in player.pieces:
        if piece.piece_id not in move.piece_ids:
            if piece.position == destination:
                own_count += 1
    
    if own_count + len(selected_pieces) > 2:
        return False
    
    if HOME_START <= destination <= HOME_END:
        return True
    
    square = to_absolute(player.color, destination)
    if is_safe_square(square):
        return True
    
    pieces_at_square = pieces_at(state, square)
    opponents_at_square = []
    for piece in pieces_at_square:
        if piece.player_id != player.player_id:
            opponents_at_square.append(piece)
    
    if len(opponents_at_square) == 0:
        return True
    
    return len(selected_pieces) == len(opponents_at_square)

def legal_moves(state: GameState, dice_roll: int) -> list[Move]:
    validate_roll(dice_roll)

    player = state.current_player()
    moves = []
    candidates = []

    for piece in player.pieces:
        candidates.append(Move(player.player_id, (piece.piece_id, )))
    
    for first, second in combinations(player.pieces, 2):
        if first.position == second.position:
            if first.position not in (YARD, FINISHED):
                candidates.append(
                    Move(player.player_id, (first.piece_id, second.piece_id))
                )
    
    for move in candidates:
        # Where would those pieces go with this roll?
        destination = move_destination(state, move, dice_roll)
        
        if destination is None:
            continue
        
        if len(move.piece_ids) == 1:
            # Which pieces does this move refer to?
            _, selected = get_move_pieces(state, move)
            position = selected[0].position

            # If moving one piece, is there a blockade in this path?
            if single_path_blocked(state, player.player_id, position, destination):
                continue

        # Can those piece occupy the destination?
        if can_land(state, move, destination):
            moves.append(move)

    return moves
