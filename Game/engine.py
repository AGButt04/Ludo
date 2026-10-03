from Game.models import GameState, Move
from Game.rules import get_move_pieces, legal_moves, move_destination
from Game.rules import to_absolute, is_safe_square, has_won, pieces_at
from Game.constants import YARD

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
    
    
