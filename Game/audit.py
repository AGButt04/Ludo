from Game.models import GameState
from pathlib import Path
import json

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

def make_transition(before, move, after, choices=(), turn=None) -> dict:
    transition = {
        "before": before,
        "move": None,
        "after": after,
        "event": "pass" if move is None else "move",
        "turn": turn,
        "legal_choices": [
            {"player_id": choice.player_id, "piece_ids": list(choice.piece_ids)}
            for choice in choices
        ],
    }

    if move is not None:
        transition["move"] = {
            "player_id": move.player_id,
            "piece_ids": list(move.piece_ids),
        }

    return transition


def save_trace(trace: list[dict], path: str) -> None:
    """Save one game's audit records without replacing an existing file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    with target.open("x", encoding="utf-8") as file:
        for record in trace:
            file.write(json.dumps(record) + "\n")
