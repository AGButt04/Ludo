from Game.models import GameResult
from run_game import run_game
from Experiments.results_io import save_result, load_results
from Experiments.run_config import prepare_run
from pathlib import Path

def run_batch(num_games: int, output_path: str, base_seed: int = 0, num_players: int = 4, max_turns: int = 10000) -> list[GameResult]:
    for name, value in (
        ("num_games", num_games),
        ("base_seed", base_seed),
        ("num_players", num_players),
        ("max_turns", max_turns)
    ):    
        if type(value) is not int:
            raise TypeError(f"{name} must be an integer")

    if num_games <= 0 or max_turns <= 0:
        raise ValueError("num_games and max_turns must be positive")

    if num_players not in (2, 4):
        raise ValueError("num_players must be 2 or 4")
    
    if Path(output_path).exists():
        raise FileExistsError("Use a new output file for this batch.")
    
    results = []

    for game in range(num_games):
        seed = base_seed + game
        starting_player_index = game % num_players

        result = run_game(num_players, seed, max_turns, starting_player_index)
        results.append(result)
        save_result(result, output_path)
    
    return results

def summarize_results(results: list[GameResult]) -> dict:
    if results:
        num_players = results[0].num_players

        if any(result.num_players != num_players for result in results):
            raise ValueError("Cannot combine two-player and four-player results.")

    completed = 0
    cutoffs = 0
    total_turns = 0
    total_moves = 0
    wins = {}
    total_games = len(results)

    if results:
        for player_id in range(num_players):
            wins[player_id] = 0
    
    for result in results:
        total_moves += result.moves_played
        total_turns += result.turns_played

        if result.truncated:
            cutoffs += 1
        else:
            completed += 1
            wins[result.winner_id] += 1

    player_win_rate = {}
    for player_id, win_count in wins.items():
        player_win_rate[player_id] = win_count / completed if completed > 0 else None

    # These averages include cutoff games; win rates use only completed games.
    avg_turns = total_turns / total_games if total_games > 0 else None
    avg_moves = total_moves / total_games if total_games > 0 else None

    return {
        "total_games": total_games,
        "completed_games": completed,
        "cutoffs": cutoffs,
        "wins_by_player": wins,
        "win_rates_completed_games": player_win_rate,
        "average_turns_all_games": avg_turns,
        "average_moves_all_games": avg_moves,
    }

def run_experiment(
    target_games: int,
    run_dir: str, 
    base_seed: int = 0, 
    num_players: int = 4,
    max_turns: int = 10000,
    max_new_games = None
) -> list[GameResult]:

    if type(target_games) is not int:
        raise TypeError("Target games must be an integer.")
    if target_games <= 0:
        raise ValueError("Target games must be positive.")

    if max_new_games is not None:
        if type(max_new_games) is not int:
            raise TypeError("Max new games must be an integer.")
        if max_new_games <= 0:
            raise ValueError("Max new games must be positive.")

    results_path = prepare_run(run_dir, base_seed, num_players, max_turns)

    if results_path.exists():
        results = load_results(str(results_path))
    else:
        results = []
    
    saved_game_ids = set()

    for result in results:
        if type(result.seed) is not int:
            raise ValueError("Saved seed must be an integer.")

        game_id = result.seed - base_seed

        if not 0 <= game_id < target_games:
            raise ValueError("Saved game ID is outside the requested range.")

        if result.num_players != num_players or result.max_turns != max_turns:
            raise ValueError("Saved game settings do not match this experiment.")

        if result.starting_player_index != game_id % num_players:
            raise ValueError("Saved game has the wrong starting player.")

        if game_id in saved_game_ids:
            raise ValueError("This game appears more than once in the results.")
        
        if type(result.truncated) is not bool:
            raise ValueError("Saved cutoff status must be a boolean.")

        if result.truncated:
            if result.winner_id is not None:
                raise ValueError("A cutoff game cannot have a winner.")
        else:
            if type(result.winner_id) is not int:
                raise ValueError("A completed game must have an integer winner ID.")

            if not 0 <= result.winner_id < num_players:
                raise ValueError("Winner ID must identify a participating player.")
        
        saved_game_ids.add(game_id)
    
    new_games = 0

    for game_id in range(target_games):
        if game_id in saved_game_ids:
            continue

        if max_new_games is not None and new_games >= max_new_games:
            break

        result = run_game(
            num_players=num_players,
            seed=base_seed + game_id,
            max_turns=max_turns,
            starting_player_index=game_id % num_players,
        )

        save_result(result, str(results_path))
        results.append(result)
        new_games += 1
    
    results.sort(key=lambda result: result.seed)
    return results


