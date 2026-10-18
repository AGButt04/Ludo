from Game.models import GameState, Move
from Game.rules import get_move_pieces, legal_moves, move_destination
from Game.rules import to_absolute, is_safe_square, has_won, pieces_at
from Game.constants import YARD
from Game.dice import Dice

def apply_move(state: GameState, move: Move, dice_roll: int) -> None:
    # This method applies the chosen move and change the game state.

    # First, we check if the game is over.
    for player in state.players:
        if has_won(state, player.player_id):
            raise ValueError("The game has already ended.")

    # Resolve the move's player and selected pieces; legality checks their turn below.
    player, selected_pieces = get_move_pieces(state, move)
    # Get the legal moves the player can take in the current state.
    choices = legal_moves(state, dice_roll)
    is_legal = False

    for choice in choices:
        # Then here we check if the move that player wants to 
        # make is actually valid or not?
        same_player = choice.player_id == move.player_id
        # Pair IDs may appear in either order: (0, 1) and (1, 0) select the same pieces.
        same_pieces = set(choice.piece_ids) == set(move.piece_ids)

        if same_player and same_pieces:
            is_legal = True
            break

    # Reject an illegal choice before changing any piece positions.
    if not is_legal:
        raise ValueError("This move is not legal.")
    
    # Then we retrive the move's destination and convert into absolute.
    move_des = move_destination(state, move, dice_roll)
    abs_pos = to_absolute(player.color, move_des)

    # Capture only on unsafe shared squares; home/finish map to None.
    if abs_pos is not None and not is_safe_square(abs_pos):
        opp_pieces = pieces_at(state, abs_pos)

        # Loop over all the pieces at the square to see if it is opponent's
        for op in opp_pieces:   
            if op.player_id != move.player_id:
                op.position = YARD
    
    # Update every selected piece, whether or not a capture occurred.
    for piece in selected_pieces:
        piece.position = move_des
    
def roll_turn(state: GameState, dice: Dice) -> None:
    # Collect the full turn's rolls before any moves; three sixes cancel the turn.

    # First, we check if the game is not over.
    for player in state.players:
        if has_won(state, player.player_id):
            raise ValueError("The game has already ended.")

    # Reject rerolling while either a current roll or later rolls remain unused.
    if state.dice_roll is not None or state.remaining_rolls:
        raise ValueError("Use the existing rolls before rolling again.")
    
    # Collect rolls until a non-six or the third consecutive six.
    rolls = []
    while True:
        # We roll and append the roll to the rolls.
        new_roll = dice.roll()
        rolls.append(new_roll)

        # If it was not a six, then we get out cuz no more rolls.
        if new_roll != 6:
            break

        # Reaching this point means the new roll is six; three rolls here are all sixes.
        # Discard them and advance the player without moving any pieces.
        if len(rolls) == 3:
            state.dice_roll = None
            state.remaining_rolls = []
            state.current_player_index = (state.current_player_index + 1) % len(state.players)
            return

    # Store the first roll for the next choice, and the later rolls in order.
    state.dice_roll = rolls[0]
    state.remaining_rolls = rolls[1:]

def play_turn(state: GameState, move: Move | None) -> None:
    # Resolve one supplied choice or forced pass, then consume the current stored roll.

    # First, again we check for the game continuation.
    for player in state.players:
        if has_won(state, player.player_id):
            raise ValueError("The game has already ended.")

    # Reject playing without a pending roll.
    if state.dice_roll is None:
        raise ValueError("Roll before choosing a move.")

    # Then we retrieve the legal moves using this roll for 
    # the current player in the current state.
    moves = legal_moves(state, state.dice_roll)

    # None is allowed only when no legal move exists; it still consumes the roll below.
    if move is None:
        if moves:
            raise ValueError("You must choose a move when one is available.")
    else:
        # Else we apply the move and change tha game state.
        apply_move(state, move, state.dice_roll)

    # A winner ends the game immediately; discard unused rolls without advancing.
    if has_won(state, state.current_player().player_id):
        state.dice_roll = None
        state.remaining_rolls = []
        return

    # If there are some remaining rolls then we do
    # not change the player but just update the roll
    if state.remaining_rolls:
        state.dice_roll = state.remaining_rolls.pop(0)
    else:
        # Else we change the player's turn and make current roll = None.
        state.dice_roll = None
        state.current_player_index = (state.current_player_index + 1) % len(state.players)
 
