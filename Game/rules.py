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
    # Calculate a single piece's destination; path and landing legality are checked separately.

    validate_position(position) # Accept relative progress from yard through finish (0–57).
    validate_roll(dice_roll) # Validate if the roll is in between 1 - 6.

    if position == YARD and dice_roll == 6:
        # If just rolled a six and position was YARD. Get it out.
        return TRACK_START
    elif position == YARD:
        # A piece in the yard cannot leave without a six.
        return None
    elif position == FINISHED:
        # If already finished, then no more moves.
        return None
    else:
        # Else new position is current pos + roll
        new_pos = position + dice_roll
        return new_pos if (new_pos <= FINISHED) else None

def to_absolute(color: Color, position: int) -> int | None:
    # This method converts a relative position of the 
    # piece progress to absolute according to the board.

    validate_color(color)
    validate_position(position)

    if position < TRACK_START or position > TRACK_END:
        # Yard, private home path, and finish have no shared-track square.
        return None
    
    start = START_SQUARES[color] # We need the absolute starting point for the piece.
    # Use zero-based offsets, wrap around the track, then return a 1-based square.
    return ((start - 1 + position - 1) % TRACK_LENGTH) + 1

def pieces_at(state: GameState, square: int) -> list[Piece]:
    # Return existing Piece objects from all players on this absolute shared square.

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
    # Check whether an absolute square is safe, regardless of occupancy.

    validate_square(square)
    return square in SAFE_SQUARES

def count_pieces_at(state: GameState, square: int, player_id: int) -> int:
    # Count only this player's pieces on the absolute shared square.
    
    get_player(state, player_id) # Reject a player ID that is not in this game.

    pieces = pieces_at(state, square)
    count = 0
    for piece in pieces:
        if piece.player_id == player_id:
            count += 1
    
    return count
 
def shared_path(color: Color, position: int, destination: int) -> list[int]:
    # Return crossed absolute shared squares; 
    # exclude the origin and include a shared destination.

    # Validations of color, position, and destination. 
    validate_color(color)
    validate_position(position)
    validate_position(destination)
    
    if position >= destination:
        # Destination must be strictly ahead in relative progress.
        raise ValueError("The position has to be less than the destination.")

    squares = []

    # Walk relative progress from the next position through the destination.
    for rel_pos in range(position + 1, destination + 1):
        abs_pos = to_absolute(color, rel_pos)

        # Skip yard/home/finish positions, which have no shared-track square.
        if abs_pos is not None:
            squares.append(abs_pos)
    
    return squares

def has_blockade(state: GameState, square: int, player_id: int) -> bool:
    # Check whether the specified player owns a pair on this absolute square.

    count = count_pieces_at(state, square, player_id)

    if count > 2:
        # More than two same-player pieces on a shared square violates our rules.
        raise ValueError("Stacks larger than two are not supported yet")

    return count == 2

def opponent_blockade_at(state: GameState, square: int, player_id: int) -> bool:
    # Check for a pair owned by anyone except player_id, even on a safe square.

    get_player(state, player_id) # Validate the player. 
    validate_square(square) # Validate the square.

    exist = False

    # Loop over all the players in the game
    for player in state.players:
        # Skip the specified player; check only their opponents.
        if player.player_id == player_id:
            continue
        
        # Stop searching after finding an opponent's pair.
        if has_blockade(state, square, player.player_id):
            exist = True
            break
    
    return exist

def single_path_blocked(state: GameState, player_id: int, position: int, destination: int) -> bool:
    # Check whether an opposing pair blocks a single piece 
    # on its shared path, including landing.
    
    moving_player = get_player(state, player_id)

    squares = shared_path(moving_player.color, position, destination)
    for square in squares:
        # Opposing pairs on this safe square do not block passage or landing.
        if is_safe_square(square):
            continue

        # If opponent's blockade in the path, can't move, return True.
        if opponent_blockade_at(state, square, player_id):
            return True
    
    return False

def move_destination(state: GameState, move: Move, dice_roll: int) -> int | None:
    # Calculate the selected single/pair's relative destination without changing state.
    
    validate_roll(dice_roll)
    
    # Get the player and its selected pieces from the move in the state. 
    player, selected_pieces = get_move_pieces(state, move)

    if len(selected_pieces) == 1:
        # If there is only one piece, then we can 
        # determine that using destination_for_roll method.
        
        return destination_for_roll(selected_pieces[0].position, dice_roll)
    else:
        # Two pieces were selected: check only moving them together, not splitting.

        first, second = selected_pieces

        # If not a pair, then return None.
        if first.position != second.position:
            return None
        
        # Both share a position; pairs cannot leave the yard or move after finishing.
        if first.position in (YARD, FINISHED):
            return None
        
        # If the dice is not a multiple of 2 then a blockade can't move.
        if dice_roll % 2 != 0:
            return None
        
        # Else calculate the blockade's destionation and return.
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

def has_won(state: GameState, player_id: int) -> bool:
    player = get_player(state, player_id)

    return all(piece.position == FINISHED for piece in player.pieces)
