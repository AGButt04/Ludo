from Game.models import GameState, Move
from Game.rules import get_move_pieces, legal_moves, move_destination
from Game.rules import to_absolute, is_safe_square, has_won, pieces_at
from Game.constants import YARD
from Game.dice import Dice

def apply_move(state: GameState, move: Move, dice_roll: int) -> None:
    for player in state.players:
        if has_won(state, player.player_id):
            raise ValueError("The game has already ended.")

    player, selected_pieces = get_move_pieces(state, move)
    choices = legal_moves(state, dice_roll)
    is_legal = False

    for choice in choices:
        same_player = choice.player_id == move.player_id
        same_pieces = set(choice.piece_ids) == set(move.piece_ids)

        if same_player and same_pieces:
            is_legal = True
            break

    if not is_legal:
        raise ValueError("This move is not legal.")
    
    move_des = move_destination(state, move, dice_roll)
    abs_pos = to_absolute(player.color, move_des)

    if abs_pos is not None and not is_safe_square(abs_pos):
        opp_pieces = pieces_at(state, abs_pos)
        for op in opp_pieces:   
            if op.player_id != move.player_id:
                op.position = YARD
    
    for piece in selected_pieces:
        piece.position = move_des
    
def roll_turn(state: GameState, dice: Dice) -> None:
    for player in state.players:
        if has_won(state, player.player_id):
            raise ValueError("The game has already ended.")

    if state.dice_roll is not None or state.remaining_rolls:
        raise ValueError("Use the existing rolls before rolling again.")
    
    rolls = []
    while True:
        new_roll = dice.roll()
        rolls.append(new_roll)

        if new_roll != 6:
            break

        if len(rolls) == 3:
            state.dice_roll = None
            state.remaining_rolls = []
            state.current_player_index = (state.current_player_index + 1) % len(state.players)
            return

    state.dice_roll = rolls[0]
    state.remaining_rolls = rolls[1:]

def play_turn(state: GameState, move: Move | None) -> None:
    for player in state.players:
        if has_won(state, player.player_id):
            raise ValueError("The game has already ended.")

    if state.dice_roll is None:
        raise ValueError("Roll before choosing a move.")

    moves = legal_moves(state, state.dice_roll)

    if move is None:
        if moves:
            raise ValueError("You must choose a move when one is available.")
    else:
        apply_move(state, move, state.dice_roll)

    if has_won(state, state.current_player().player_id):
        state.dice_roll = None
        state.remaining_rolls = []
        return

    if state.remaining_rolls:
        state.dice_roll = state.remaining_rolls.pop(0)
    else:
        state.dice_roll = None
        state.current_player_index = (state.current_player_index + 1) % len(state.players)
