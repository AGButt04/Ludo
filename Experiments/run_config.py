import json
from pathlib import Path

def prepare_run(
    run_dir: str, 
    base_seed: int, 
    num_players: int, 
    max_turns: int
) -> Path:

    if type(run_dir) is not str:
        raise TypeError("Run dir must be a string.")
    if type(base_seed) is not int:
        raise TypeError("Base Seed must be an integer.")
    if type(num_players) is not int:
        raise TypeError("Number of players must be an integer.")
    if type(max_turns) is not int:
        raise TypeError("Max turns must be an integer.")
    if num_players not in (2, 4):
        raise ValueError("Number of players must be 2 or 4.")
    if max_turns <= 0:
        raise ValueError("Max turns must be positive.")

    folder = Path(run_dir)
    config_path = folder / "config.json"
    results_path = folder / "games.jsonl"

    config = {
        "base_seed": base_seed,
        "num_players": num_players,
        "max_turns": max_turns,
        "schema_version": 2,
        "rules_version": 1,
        "agent_type": "random",
        "starting_seat_policy": "rotate"
        "max_invalid_attempts": 3,
        "invalid_action_policy": "forfeit_remaining_turn"
    }

    if config_path.exists():
        # Existing run: read its settings without overwriting them.
        with config_path.open("r", encoding="utf-8") as file:
            saved_config = json.load(file)

        if saved_config != config:
            raise ValueError("This run already has different settings. Use a new run directory.")
        
        # Python treats True == 1; stored setting types must match too.
        if any(type(saved_config[key]) is not type(value) for key, value in config.items()):
            raise ValueError("Saved config contains incorrect setting types.")
    else:
        if results_path.exists():
            raise ValueError("Results exist without a config; cannot assign new settings.")

        folder.mkdir(parents=True, exist_ok=True)
        with config_path.open("x", encoding="utf-8") as file:
            json.dump(config, file, indent=2)
            file.write("\n")

    # Return the location; the results file is created when a game is saved.
    return results_path
