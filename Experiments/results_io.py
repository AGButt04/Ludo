from dataclasses import asdict
from pathlib import Path
import json
from Game.models import GameResult

def save_result(result: GameResult, path: str) -> None:
    """Append one game summary without overwriting earlier games."""
    validate_results(result)
    dict_result = asdict(result)
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(dict_result) + "\n")


def load_results(path: str) -> list[GameResult]:
    """Read each nonblank JSON line back into a GameResult."""
    results = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            data = json.loads(line)
            result = GameResult(**data)
            validate_results(result)
            results.append(result)

    return results

def validate_results(result: GameResult) -> None:
    if type(result.turns_played) is not int:
        raise TypeError("Turns played has to be an integer.")

    if result.turns_played <= 0:
        raise ValueError("Turns played must be positive.")

    if type(result.moves_played) is not int:
        raise TypeError("Moves played has to be an integer.")
    
    if result.moves_played < 0:
        raise ValueError("Moves played cannot be negative.")

    if type(result.invalid_choices) is not int:
        raise TypeError("Invalid Choices has to be an integer.")

    if result.invalid_choices < 0:
        raise ValueError("Invalid choices cannot be negative.")

    if type(result.forfeited_turns) is not int:
        raise TypeError("Forfeited turns has to be an integer.")

    if result.forfeited_turns < 0:
        raise ValueError("Forfeited turns cannot be negative.")

    if type(result.max_turns) is not int:
        raise TypeError("Max turns has to be an integer.")

    if result.max_turns <= 0:
        raise ValueError("Max turns must be positive.")

    if result.turns_played > result.max_turns:
        raise ValueError("Turns played cannot exceed max turns.")

    if result.forfeited_turns > result.turns_played:
        raise ValueError("Forfeited turns cannot exceed turns played.")

    if type(result.num_players) is not int:
        raise TypeError("Number of players must be an integer.")

    if result.num_players not in (2, 4):
        raise ValueError("Number of players must be 2 or 4.")

    if type(result.starting_player_index) is not int:
        raise TypeError("Starting player index must be an integer.")

    if not 0 <= result.starting_player_index < result.num_players:
        raise ValueError("Starting player index is outside the player range.")

    if type(result.truncated) is not bool:
        raise TypeError("Truncated must be a boolean.")
    if result.truncated:
        if result.winner_id is not None:
            raise ValueError("A cutoff game cannot have a winner.")
        if result.turns_played != result.max_turns:
            raise ValueError("A cutoff game must reach max turns.")
    else:
        if type(result.winner_id) is not int:
            raise TypeError("Winner ID's type must be an integer.")
        if not 0 <= result.winner_id < result.num_players:
            raise ValueError("Winner ID is outside the player range.")
    
    if not result.truncated and result.moves_played == 0:
        raise ValueError("A completed win must include at least one move.")

    if type(result.seed) is not int:
        raise TypeError("The seed must be an integer.")

    if result.invalid_choices < 3 * result.forfeited_turns:
        raise ValueError("Each forfeited turn requires three invalid choices.")

    if result.moves_played > 3 * result.turns_played:
        raise ValueError("Moves played cannot exceed three per turn.")

    if result.invalid_choices > 2 * result.moves_played + 3 * result.forfeited_turns:
        raise ValueError("Invalid choices exceed the allowed attempts for moves and forfeitures.")
