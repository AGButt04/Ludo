from Game.models import GameState

def snapshot_state(state: GameState) -> dict:
    curr_state = {
        "current_player_id": state.current_player().player_id,
        "dice_roll": state.dice_roll,
        "remaining_rolls": state.remaining_rolls.copy(),
        "pieces": []
    }

    for player in state.players:
        for piece in player.pieces:
            piece_dict = {
                "player_id": player.player_id,
                "piece_id": piece.piece_id,
                "position": piece.position
            }
            
            curr_state["pieces"].append(piece_dict)
    
    return curr_state